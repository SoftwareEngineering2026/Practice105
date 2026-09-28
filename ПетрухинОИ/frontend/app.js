const textInput = document.getElementById("textInput");
const submitButton = document.getElementById("submitButton");
const charCount = document.getElementById("charCount");
const message = document.getElementById("message");
const resultSection = document.getElementById("resultSection");
const taskIdElement = document.getElementById("taskId");
const taskStatusElement = document.getElementById("taskStatus");
const resultOutput = document.getElementById("resultOutput");
let pollingTimer = null;

textInput.addEventListener("input", () => {
  charCount.textContent = `${textInput.value.length} / 50000`;
});

function showMessage(text, type = "info") {
  message.textContent = text;
  message.className = `message ${type}`;
}

function setLoading(loading) {
  submitButton.disabled = loading;
  submitButton.textContent = loading ? "Создание задачи..." : "Запустить анализ";
}

async function createTask() {
  const text = textInput.value.trim();
  if (!text) {
    showMessage("Введите текст перед запуском анализа.", "error");
    return;
  }
  setLoading(true);
  resultSection.classList.remove("hidden");
  resultOutput.textContent = "";
  taskStatusElement.textContent = "создание задачи";
  try {
    const response = await fetch("/api/tasks", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({text})
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Backend вернул ошибку.");
    taskIdElement.textContent = data.task_id;
    taskStatusElement.textContent = data.status;
    showMessage("Задача поставлена в очередь. Worker обработает её отдельно.", "success");
    if (pollingTimer) clearTimeout(pollingTimer);
    pollStatus(data.task_id);
  } catch (error) {
    showMessage(error.message, "error");
    taskStatusElement.textContent = "ошибка";
  } finally {
    setLoading(false);
  }
}

async function pollStatus(taskId) {
  try {
    const response = await fetch(`/api/tasks/${taskId}`);
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Не удалось получить статус задачи.");
    taskStatusElement.textContent = data.status;
    if (data.status === "completed") {
      resultOutput.textContent = JSON.stringify(data.result, null, 2);
      showMessage("Обработка завершена.", "success");
      return;
    }
    if (data.status === "failed") {
      resultOutput.textContent = data.error || "Worker сообщил об ошибке.";
      showMessage("Во время обработки произошла ошибка.", "error");
      return;
    }
    pollingTimer = setTimeout(() => pollStatus(taskId), 1000);
  } catch (error) {
    showMessage(error.message, "error");
  }
}

submitButton.addEventListener("click", createTask);
