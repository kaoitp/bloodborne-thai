"""Bloodborne message archives: DCX (zlib) -> BND4 -> FMG (version 2) read and write."""
import struct
import zlib


def dcx_read(data):
    if data[:4] != b'DCX\0' or data[0x28:0x2C] != b'DFLT':
        raise ValueError('not a DCX/DFLT file')
    size, compressed = struct.unpack_from('>II', data, 0x1C)
    start = data.index(b'DCA\0', 0x2C) + 8
    out = zlib.decompress(data[start:start + compressed])
    if len(out) != size:
        raise ValueError('DCX size mismatch')
    return out


def dcx_write(original, payload):
    """New DCX with the header of `original` and `payload` as content."""
    start = original.index(b'DCA\0', 0x2C) + 8
    compressed = zlib.compress(payload, 9)
    header = bytearray(original[:start])
    struct.pack_into('>II', header, 0x1C, len(payload), len(compressed))
    return bytes(header) + compressed


ENTRY = struct.Struct('<IiQQIiI')   # flags, -1, compressed size, size, data offset, id, name offset


class Bnd4:
    def __init__(self, data):
        if data[:4] != b'BND4' or struct.unpack_from('<Q', data, 0x20)[0] != ENTRY.size:
            raise ValueError('unexpected BND4 layout')
        self.data = data
        count = struct.unpack_from('<I', data, 0x0C)[0]
        self.entries = [list(ENTRY.unpack_from(data, 0x40 + i * ENTRY.size)) for i in range(count)]
        self.data_start = min(e[4] for e in self.entries)
        self.files = {e[5]: data[e[4]:e[4] + e[2]] for e in self.entries}

    def name(self, file_id):
        offset = next(e[6] for e in self.entries if e[5] == file_id)
        end = offset
        while self.data[end:end + 2] != b'\0\0':
            end += 2
        return self.data[offset:end].decode('utf-16le').replace('\\', '/').rsplit('/', 1)[-1]

    def build(self):
        out = bytearray(self.data[:self.data_start])
        for index, entry in enumerate(self.entries):
            content = self.files[entry[5]]
            out += b'\0' * (-len(out) % 16)
            entry[2] = entry[3] = len(content)
            entry[4] = len(out)
            ENTRY.pack_into(out, 0x40 + index * ENTRY.size, *entry)
            out += content
        return bytes(out)


class Fmg:
    """strings: {id: text or None} in file order; groups of consecutive ids are rebuilt on write."""

    def __init__(self, data):
        if data[2] != 2 or data[1] != 0:
            raise ValueError('only little-endian FMG version 2 is supported')
        self.header = data[:0x28]
        groups, count = struct.unpack_from('<II', data, 0x0C)
        table = struct.unpack_from('<Q', data, 0x18)[0]
        offsets = struct.unpack_from(f'<{count}Q', data, table)
        self.strings = {}
        for g in range(groups):
            index, first, last, _ = struct.unpack_from('<IIII', data, 0x28 + g * 16)
            for string_id in range(first, last + 1):
                offset = offsets[index + string_id - first]
                if offset:
                    end = offset
                    while data[end:end + 2] != b'\0\0':
                        end += 2
                    self.strings[string_id] = data[offset:end].decode('utf-16le')
                else:
                    self.strings[string_id] = None

    def build(self):
        ids = list(self.strings)
        groups = []
        for index, string_id in enumerate(ids):
            if groups and groups[-1][2] + 1 == string_id:
                groups[-1][2] = string_id
            else:
                groups.append([index, string_id, string_id])
        table = 0x28 + 16 * len(groups)
        pos = table + 8 * len(ids)
        offsets, blob = [], bytearray()
        for string_id in ids:
            text = self.strings[string_id]
            if text is None:
                offsets.append(0)
            else:
                offsets.append(pos + len(blob))
                blob += text.encode('utf-16le') + b'\0\0'
        blob += b'\0' * (-len(blob) % 4)
        out = bytearray(self.header)
        struct.pack_into('<I', out, 4, pos + len(blob))
        struct.pack_into('<II', out, 0x0C, len(groups), len(ids))
        struct.pack_into('<Q', out, 0x18, table)
        for group in groups:
            out += struct.pack('<IIII', *group, 0)
        out += struct.pack(f'<{len(ids)}Q', *offsets) + blob
        return bytes(out)
