const form = document.getElementById("avatar-form");
const nameInput = document.getElementById("name-input");
const statusEl = document.getElementById("status");
const resultEl = document.getElementById("result");

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const name = nameInput.value.trim();
  if (!name) return;

  resultEl.innerHTML = "";
  statusEl.textContent = "Отправка задачи...";

  try {
    const response = await fetch("/api/avatars", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name }),
    });

    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.error || "Ошибка сервера");
    }

    const { task_id } = await response.json();
    statusEl.textContent = "Аватар генерируется...";
    pollStatus(task_id);
  } catch (error) {
    statusEl.textContent = `Ошибка: ${error.message}`;
  }
});

function pollStatus(taskId) {
  const interval = setInterval(async () => {
    try {
      const response = await fetch(`/api/avatars/${taskId}`);
      const data = await response.json();

      if (data.status === "success") {
        clearInterval(interval);
        statusEl.textContent = "Готово!";
        resultEl.innerHTML = `<img src="${data.avatar_url}" alt="Аватар" class="avatar" />`;
      } else if (data.status === "failure") {
        clearInterval(interval);
        statusEl.textContent = `Ошибка генерации: ${data.error || ""}`;
      } else {
        statusEl.textContent = "Аватар генерируется...";
      }
    } catch (error) {
      clearInterval(interval);
      statusEl.textContent = `Ошибка: ${error.message}`;
    }
  }, 1000);
}
