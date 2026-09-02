document.addEventListener("DOMContentLoaded", function () {
    var modalElement = document.getElementById("deleteConfirmModal");
    var modal = new bootstrap.Modal(modalElement);
    var targetTaskId = null;

    document.querySelectorAll("[data-task-id]").forEach(function (button) {
        button.addEventListener("click", function () {
            targetTaskId = button.getAttribute("data-task-id");
            var title = button.getAttribute("data-task-title") || "";
            document.getElementById("deleteConfirmTaskTitle").textContent = title;
            modal.show();
        });
    });

    document
        .getElementById("deleteConfirmButton")
        .addEventListener("click", function () {
            if (!targetTaskId) {
                return;
            }
            fetch("/tasks/" + targetTaskId, { method: "DELETE" })
                .then(function (response) {
                    if (response.ok) {
                        window.location.reload();
                    } else {
                        alert("削除に失敗しました。");
                    }
                })
                .catch(function () {
                    alert("削除に失敗しました。");
                });
        });
});