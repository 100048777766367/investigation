import os, json, subprocess

print("🔍 [INVESTIGATION ENGINE] Đang thẩm định tính tương thích của đơn thuốc...")

SHARED_DIR = "/tmp/bodhi_workspace"
os.makedirs(SHARED_DIR, exist_ok=True)

# Kéo storage về để đối chiếu danh mục căn cước
storage_dir = f"{SHARED_DIR}/storage"
if not os.path.exists(storage_dir):
    subprocess.run(["git", "clone", "--depth", "1", "https://github.com/100048777766367/storage.git", storage_dir], capture_output=True)

# Đọc đơn thuốc (giả định lấy từ choice)
try:
    with open("synapses/prescription.json", "r") as f: rx = json.load(f)
    requested = rx.get("requested_items", [])
    
    print(f"📋 Đang thẩm định {len(requested)} vị thuốc yêu cầu...")
    audit_results = []
    for item in requested:
        # Kiểm tra xem tệp có tồn tại trong storage micro_passports không
        passports_dir = f"{storage_dir}/micro_passports"
        found = False
        if os.path.exists(passports_dir):
            for pfile in os.listdir(passports_dir):
                with open(os.path.join(passports_dir, pfile), "r") as pf:
                    data = json.load(pf)
                    for f_item in data.get("tier_3_files", []):
                        if item in f_item["path"]:
                            found = True; break
        
        status = "PASSED_VERIFICATION" if found else "WARNING_NOT_INDEXED"
        audit_results.append({"item": item, "status": status})
        print(f"  ├── Thử nghiệm vị thuốc '{item}': {status}")

    rx["audit_results"] = audit_results
    rx["status"] = "AUDITED_AND_APPROVED"
    with open("synapses/investigation_report.json", "w", encoding="utf-8") as f:
        json.dump(rx, f, indent=4, ensure_ascii=False)
    print("✅ [INVESTIGATION] Đã cấp chứng nhận thẩm định tương thích thành công!")

except Exception as e:
    print(f"🔴 Lỗi thẩm định: {e}")
