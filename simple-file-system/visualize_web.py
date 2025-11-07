from flask import Flask, render_template, jsonify
import struct
import os

app = Flask(__name__)

BLOCK_SIZE = 4096
MAGIC_NUMBER = 0xf0f03410
POINTERS_PER_INODE = 5
INODES_PER_BLOCK = 128
INODE_SIZE = 48  # actual struct size for this project

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
        magic, blocks, inode_blocks, inodes = struct.unpack("<IIII", sb[:16])

        if magic != MAGIC_NUMBER:
            return jsonify({"error": "Invalid filesystem magic number"}), 400

        # build layout array
        layout = [{"id": i, "type": "data_free"} for i in range(blocks)]
        layout[0]["type"] = "super"

        for i in range(inode_blocks):
            layout[1 + i]["type"] = "inode"

        # parse inodes safely
        for b in range(inode_blocks):
            f.seek((1 + b) * BLOCK_SIZE)
            block = f.read(BLOCK_SIZE)
            for j in range(0, BLOCK_SIZE, INODE_SIZE):
                inode = block[j:j + INODE_SIZE]
                if len(inode) < 4:
                    continue
                valid = struct.unpack("<I", inode[:4])[0]
                if not valid:
                    continue

                size = struct.unpack("<I", inode[4:8])[0]
                direct = struct.unpack("<" + "I" * POINTERS_PER_INODE, inode[8:28])
                indirect = struct.unpack("<I", inode[28:32])[0]

                for d in direct:
                    if 0 < d < blocks:
                        layout[d]["type"] = "data_used"

                if 0 < indirect < blocks:
                    layout[indirect]["type"] = "indirect"

    return jsonify({
        "superblock": {
            "magic": hex(magic),
            "blocks": blocks,
            "inode_blocks": inode_blocks,
            "inodes": inodes
        },
        "blocks": layout
    })

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
