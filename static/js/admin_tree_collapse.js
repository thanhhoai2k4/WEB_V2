document.addEventListener("DOMContentLoaded", function () {
    const toggles = document.querySelectorAll(".tree-toggle");

    toggles.forEach(toggle => {
        toggle.addEventListener("click", function (e) {
            e.preventDefault();
            e.stopPropagation();

            const tr = this.closest("tr"); // Dòng hiện tại
            const currentLevel = parseInt(this.dataset.level); // Level của dòng hiện tại
            const isExpanded = this.dataset.expanded === "true"; // Trạng thái đang mở hay đóng

            // Đổi icon và trạng thái
            this.textContent = isExpanded ? "📁" : "📂"; // Đổi icon đóng/mở
            this.dataset.expanded = isExpanded ? "false" : "true";

            // Logic tìm các con
            let nextTr = tr.nextElementSibling;
            while (nextTr) {
                // Tìm nút toggle của dòng tiếp theo để lấy level
                const nextToggle = nextTr.querySelector(".tree-toggle");
                if (!nextToggle) break; // Hết danh sách cây

                const nextLevel = parseInt(nextToggle.dataset.level);

                // Nếu gặp dòng có level nhỏ hơn hoặc bằng -> Đã sang nhánh khác -> Dừng lại
                if (nextLevel <= currentLevel) break;

                // Ẩn/Hiện dòng con
                if (isExpanded) {
                    // Nếu đang mở -> Bấm để đóng -> Ẩn hết con cháu
                    nextTr.style.display = "none";
                    // Reset icon của con về trạng thái đóng (tùy chọn)
                } else {
                    // Nếu đang đóng -> Bấm để mở -> Chỉ hiện con trực tiếp (level + 1)
                    // Hoặc hiện tất cả (đơn giản nhất là hiện tất cả dòng thuộc nhánh này)
                    nextTr.style.display = "";
                    // Lưu ý: Logic chuẩn xịn sẽ phức tạp hơn để nhớ trạng thái con,
                    // nhưng logic này đủ dùng cho nhu cầu cơ bản.
                }

                nextTr = nextTr.nextElementSibling;
            }
        });
    });
});