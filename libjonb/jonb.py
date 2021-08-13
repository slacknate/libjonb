import json
import struct

JONB_PREFIX = b"JONB"


def _unpack_from(fmt, data):
    """
    Helper function to call and return the result of struct.unpack_from
    as well as any remaining packed data that exists in our bytestring following what was unpacked.
    """
    offset = struct.calcsize(fmt)
    unpacked = struct.unpack_from(fmt, data)
    remaining = data[offset:]
    return unpacked, remaining


def _parse_header(jonb_contents):
    """
    Parse the header of a jonbin file.
    We do basic validation of the header with the jonb_PREFIX constant.
    """
    if not jonb_contents.startswith(JONB_PREFIX):
        raise ValueError("Not a valid jonbin file!")

    remaining = jonb_contents[len(JONB_PREFIX):]
    (image_count,), remaining = _unpack_from("<h", remaining)

    images = []
    for index in range(0, image_count):
        (image_name,), remaining = _unpack_from("<32s", remaining)
        images.append(image_name.rstrip(b"\x00").decode("ascii"))

    return images, remaining


def _parse_chunk(jonb_contents):
    """
    Parse a single chunk from our jonbin file.
    Honestly? No idea what a chunk is! :D
    """
    (src_x, src_y, src_width, src_height, x, y, width, height), remaining = _unpack_from("<8f", jonb_contents)
    unknown1, remaining = _unpack_from("<8I", remaining)
    (layer,), remaining = _unpack_from("<I", remaining)
    unknown2, remaining = _unpack_from("<3I", remaining)

    chunk = {"src_x", src_x, "src_y", src_y, "src_width", src_width, "src_height", src_height, "x", x,
             "y", y, "width", width, "height", height, "unknown1", unknown1, "layer", layer, "unknown2", unknown2}

    return chunk, remaining


def _parse_box(jonb_contents):
    """
    Parse a single collision box from our jonbin file.
    """
    (box_id, x, y, width, height), remaining = _unpack_from("<I4f", jonb_contents)
    box = {"id": box_id, "x": x, "y": y, "width": width, "height": height}
    return box, remaining


def _parse_jonbin(jonb_contents):
    """
    Parse the given jonbin file and return a human readable format of the collision box data.
    """
    _, remaining = _unpack_from("<BBB", jonb_contents)

    (chunk_count, hurtbox_count, hitbox_count, unkbox_count, _), remaining = _unpack_from("<Ihhhh", remaining)
    _, remaining = _unpack_from("<39H", remaining)

    chunks = []
    for i in range(chunk_count):
        chunk, remaining = _parse_chunk(remaining)
        chunks.append(chunk)

    hurtboxes = []
    for i in range(hurtbox_count):
        box, remaining = _parse_box(remaining)
        hurtboxes.append(box)

    hitboxes = []
    for i in range(hitbox_count):
        box, remaining = _parse_box(remaining)
        hitboxes.append(box)

    unkboxes = []
    for i in range(unkbox_count):
        box, remaining = _parse_box(remaining)
        unkboxes.append(box)

    return chunks, hurtboxes, hitboxes, unkboxes, remaining


def extract_collision_boxes(jonb_path, out_file=None):
    """
    Extract the collision boxes from the given jonbin file.
    We output a JSON file describing the same information, but in a more human readable form.

    Reference: https://github.com/dantarion/bbtools/blob/master/jonbin_parser.py
    """
    if out_file is None:
        out_file = jonb_path.replace(".jonbin", ".json")

    with open(jonb_path, "rb") as jonb_fp:
        jonb_contents = jonb_fp.read()

    images, remaining = _parse_header(jonb_contents)
    _, hurtboxes, hitboxes, __, ___ = _parse_jonbin(remaining)

    assert len(images) == 1

    collision_data = {"hurtboxes": hurtboxes, "hitboxes": hitboxes}
    with open(out_file, "w") as col_fp:
        json.dump(collision_data, col_fp)
