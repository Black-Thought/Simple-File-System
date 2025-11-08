# 🧱 Simple File System (SFS)

A lightweight, educational implementation of a **simple file system** written in **C++**, operating on a **virtual disk** stored as a regular file.  
This project demonstrates how a file system works internally — including **superblocks, inodes, block management, mounting, and data read/write operations** — all simulated at the user level.

---
## 🧭 Overview

The **Simple File System (SFS)** simulates a real file system inside a **virtual disk image** (`disk0.img`) divided into fixed-size 4KB blocks.  
It provides a complete environment to **format**, **mount**, **create**, **read**, **write**, and **remove** files — just like a real operating system.

This project was built to help understand how data is organized and managed at the file system level.

---

## 🧩 Architecture

User Commands (Shell)
↓
File System Layer (fs.cpp)
↓
Disk Interface Layer (disk.cpp)
↓
Virtual Disk File (disk0.img)

| Layer | Description | Files |
|--------|--------------|-------|
| **Disk Layer** | Simulates physical disk operations (block read/write) | `include/sfs/disk.h`, `src/library/disk.cpp` |
| **File System Layer** | Implements file management, metadata, and allocation logic | `include/sfs/fs.h`, `src/library/fs.cpp` |
| **Shell Interface** | Command-line interface for interaction | `src/shell/sfssh.cpp` |
| **Visualization** | Flask + D3.js web UI for visualizing disk layout | `visualize_web.py`, `templates/index.html` |

---

## 💾 Disk Layout

Each disk image is divided into 4KB blocks.  
The layout of blocks inside the virtual disk is as follows:

+-----------+-------------------+------------------+

| Block 0   | Blocks 1..N       | Remaining Blocks |

| Superblock| Inode Blocks      | Data Blocks      |

+-----------+-------------------+------------------+

| Section | Purpose |
|----------|----------|
| **Superblock (Block 0)** | Stores overall file system metadata |
| **Inode Blocks** | Contain file metadata structures (10% of total blocks) |
| **Data Blocks** | Store actual file content |

---

## ⚙️ Core Structures

### 🧭 SuperBlock

struct SuperBlock {
  uint32_t MagicNumber;  // Unique FS identifier
  uint32_t Blocks;       // Total number of blocks
  uint32_t InodeBlocks;  // Number of blocks reserved for inodes
  uint32_t Inodes;       // Total number of inodes
};

### 📂 Inode

```cpp
struct Inode {
  uint32_t Valid;           // 1 if the inode is in use
  uint32_t Size;            // File size in bytes
  uint32_t Direct[5];       // Direct data block pointers
  uint32_t Indirect;        // Pointer to indirect block
};
```

### 🧱 IndirectBlock

```cpp
struct IndirectBlock {
  uint32_t Pointers[1024];  // 1024 * 4B = 4KB block of pointers
};
```

Each file = one inode.
Supports **5 direct** + **1 indirect** block pointers (→ up to ~4 MB per file).

---

## 🌟 Features

✅ Simulated block-based virtual disk

✅ File creation, deletion, reading, and writing

✅ File system formatting and mounting

✅ Direct and indirect block addressing

✅ Free block map reconstruction during mount

✅ Built-in shell interface

✅ Web-based visualization tool

✅ Comprehensive test scripts

---

## 🏗️ Build & Run

### 🧰 Prerequisites

* Linux environment
* GCC / Clang (C++11+)
* Python 3 (for visualization)
* `make` build tool

### 🔧 Build

```bash
make
```

### ▶️ Run the File System Shell

```bash
./bin/sfssh disk0.img 64
```

Creates or opens a virtual disk of 64 blocks and starts the interactive shell.

---

## 💻 Shell Commands

| Command                             | Description                                                       |
| ----------------------------------- | ----------------------------------------------------------------- |
| `format`                            | Create a new empty file system on the disk                        |
| `mount`                             | Mount an existing file system                                     |
| `debug`                             | Print the structure of the file system (superblock, inodes, etc.) |
| `create`                            | Create a new file (allocates a free inode)                        |
| `remove <ino>`                      | Delete a file and free its data blocks                            |
| `stat <ino>`                        | Display the file’s size and status                                |
| `read <ino> <len> <offset>`         | Read bytes from file                                              |
| `write <ino> <len> <offset> <byte>` | Write data (repeated byte) to file                                |
| `copyin <host_file> <ino>`          | Import an external file into FS                                   |
| `copyout <ino> <host_file>`         | Export file from FS to host                                       |
| `cat <ino>`                         | Print file contents                                               |
| `exit` / `quit`                     | Exit the shell                                                    |

### 🧩 Example Session

```bash
./bin/sfssh disk0.img 64
format
mount
create
write 0 20 0 65
read 0 20 0
debug
remove 0
```

---

## 🌐 Visualization Tool

**Files:** `visualize_web.py`, `templates/index.html`
**Technology:** Flask (backend) + D3.js (frontend)

### ▶️ Run the Visualizer

```bash
python3 visualize_web.py
```

Then open your browser at:
👉 [http://localhost:5000](http://localhost:5000)

**Displays:**

* Superblock and inode blocks
* Data block usage (used vs. free)
* File-to-block relationships
* Visual disk layout map

---

## 🧪 Testing

The `tests/` folder includes shell scripts to automatically verify all major features.

### ▶️ Run All Tests

```bash
make test
```

**Includes Tests For:**

* `format` / `mount`
* `create`, `remove`, `stat`
* `read`, `write`
* `copyin`, `copyout`
* `debug`
* Memory leak detection (via Valgrind)

---

## 👥 Contributors

**Project:** Simple File System
**Author(s):** [Black-Thought](https://github.com/Black-Thought) and Team
**Language:** C++
**Environment:** Linux
**Visualization:** Python + D3.js
**Course / Domain:** Operating Systems, File Systems, Storage Management

---

## 🏁 Summary

This project demonstrates the **fundamental workings of a file system**, including block-level storage, metadata management, and file I/O operations.
It provides a practical foundation for understanding how real operating systems manage persistent storage.

> “From raw bytes to structured files — building a file system from scratch reveals the hidden world inside every hard drive.”
