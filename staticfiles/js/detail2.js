const detailOptionsGender = document.querySelectorAll(".gender-detail-option");
const choiceInputGender = document.querySelectorAll(".gender-choice-input");
const voteBtnGender = document.querySelector(".vote-submit-btn");

detailOptionsGender.forEach((option, index) => {
  option.addEventListener("click", () => {
    choiceInputGender.forEach((input) => {
      input.checked = false;
    });

    const radioInput = document.getElementById(`choice${index + 1}`);
    radioInput.checked = true;

    detailOptionsGender.forEach((opt) => {
      opt.classList.remove("selected");
    });
    option.classList.add("selected");

    voteBtnGender.classList.add("active");
    voteBtnGender.classList.remove("disabled");
    voteBtnGender.disabled = false;

    // 클릭 시 배경색 변경 추가
    detailOptionsGender.forEach((opt, idx) => {
      if (idx === index) {
        opt.style.backgroundColor = "var(--redpink-primary-color)";
        opt.style.color = "white";
      } else {
        opt.style.backgroundColor = "white";
        opt.style.color = "initial";
      }
    });
  });
});

// 버튼 비활성화 함수
function disableVoteButton() {
  detailOptionsGender.forEach((option) => {
    option.classList.remove("selected");
    option.style.backgroundColor = "white";
    option.style.color = "initial";
  });

  choiceInputGender.forEach((input) => {
    input.checked = false;
  });

  voteBtnGender.classList.remove("active");
  voteBtnGender.classList.add("disabled");
  voteBtnGender.disabled = true;
}
