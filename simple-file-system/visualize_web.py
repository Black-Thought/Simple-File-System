from flask import Flask, render_template, jsonify
import struct
import os
import math

app = Flask(__name__)

BLOCK_SIZE = 4096
MAGIC_NUMBER = 0xf0f03410
POINTERS_PER_INODE = 5
INODES_PER_BLOCK = 128
INODE_SIZE = 32  # 8 fields * 4 bytes each (from your project)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/data")
def get_data():
    disk_path = "disk0.img"
    if not os.path.exists(disk_path):
        return jsonify({"error": "disk0.img not found"}), 404

    with open(disk_path, "rb") as f:
        sb = f.read(BLOCK_SIZE)
        try:
            magic, blocks, inode_blocks, inodes = struct.unpack("<IIII", sb[:16])
        except struct.error:
            return jsonify({"error": "Invalid or corrupt superblock"}), 400

        if magic != MAGIC_NUMBER:
            return jsonify({"error": "Invalid filesystem magic number"}), 400

        layout = [{"id": i, "type": "data_free"} for i in range(blocks)]
        layout[0]["type"] = "super"
        for i in range(inode_blocks):
            layout[1 + i]["type"] = "inode"

        files = []
        inode_counter = 0

        # Parse inodes for real data
        for b in range(inode_blocks):
            f.seek((1 + b) * BLOCK_SIZE)
            block = f.read(BLOCK_SIZE)
            for i in range(0, BLOCK_SIZE, INODE_SIZE):
                inode = block[i:i + INODE_SIZE]
                if len(inode) < INODE_SIZE:
                    continue
                valid = struct.unpack("<I", inode[:4])[0]
                if not valid:
                    continue

                size = struct.unpack("<I", inode[4:8])[0]
                direct = struct.unpack("<" + "I" * POINTERS_PER_INODE, inode[8:28])
                indirect = struct.unpack("<I", inode[28:32])[0]

                allocated_blocks = []

                # Mark direct blocks
                for d in direct:
                    if 0 < d < blocks:
                        layout[d]["type"] = "data_used"
                        allocated_blocks.append(d)

                # Mark indirect blocks
                if 0 < indirect < blocks:
                    layout[indirect]["type"] = "indirect"
                    allocated_blocks.append(indirect)
                    f.seek(indirect * BLOCK_SIZE)
                    indirect_data = f.read(BLOCK_SIZE)
                    ptr_count = BLOCK_SIZE // 4
                    for j in range(ptr_count):
                        ptr = struct.unpack("<I", indirect_data[j*4:j*4+4])[0]
                        if 0 < ptr < blocks:
                            layout[ptr]["type"] = "data_used"
                            allocated_blocks.append(ptr)

                files.append({
                    "inode": inode_counter,
                    "name": f"file_{inode_counter}",
                    "size": size,
                    "blocks": allocated_blocks
                })
                inode_counter += 1

    # convert allocated blocks to a display string for table
    for fdata in files:
        fdata["blocks_str"] = ", ".join(map(str, fdata["blocks"])) if fdata["blocks"] else "-"

    return jsonify({
        "superblock": {
            "magic": hex(magic),
            "blocks": blocks,
            "inode_blocks": inode_blocks,
            "inodes": inodes
        },
        "blocks": layout,
        "files": files
    })

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
