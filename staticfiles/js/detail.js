const detailOptions = document.querySelectorAll(".detail-option");
const choiceInput = document.querySelectorAll(".choice-input");
const voteBtn = document.querySelector(".vote-submit-btn"); // 클래스 선택자 사용

detailOptions.forEach((option, index) => {
  option.addEventListener("click", () => {
    choiceInput.forEach((input) => {
      input.checked = false;
    });

    const radioInput = document.getElementById(`choice${index + 1}`);
    radioInput.checked = true;
    detailOptions.forEach((opt) => {
      opt.classList.remove("selected");
    });
    option.classList.add("selected");

    voteBtn.classList.add("active"); // 활성화 클래스 추가
    voteBtn.classList.remove("disabled"); // 비활성화 클래스 제거
    voteBtn.disabled = false; // 버튼 활성화
  });
});

// 버튼 비활성화 함수
function disableVoteButton() {
  voteBtn.classList.remove("active");
  voteBtn.classList.add("disabled");
  voteBtn.disabled = true;
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
