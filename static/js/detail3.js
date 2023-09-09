document.addEventListener("DOMContentLoaded", function () {
  const radioGroups = document.querySelectorAll(".mbti-two-options");

  radioGroups.forEach((group) => {
    const mbtiOptions = group.querySelectorAll(".mbti-detail-option");

    mbtiOptions.forEach((option) => {
      option.addEventListener("click", () => {
        selectMBTIOption(option);
        checkSubmitButton(radioGroups);
        updateSelectedMBTI(radioGroups);
      });
      const labelText = option.querySelector("label");
      labelText.addEventListener("click", (e) => {
        e.preventDefault();
        option.querySelector(".mbti-detail-option").click(); // 라디오 버튼 클릭 이벤트 수행
      });
    });
  });
});

function selectMBTIOption(option) {
  const isSelected = option.classList.contains("selected");

  if (!isSelected) {
    const selectedOption = option.parentElement.querySelector(
      ".mbti-detail-option.selected"
    );
    if (selectedOption) {
      selectedOption.classList.remove("selected");
    }
    option.classList.add("selected");

    // 선택한 옵션의 라디오 버튼 선택
    const radioButton = option.querySelector(".mbti-choice-input");
    radioButton.checked = true;
  } else {
    option.classList.remove("selected");
    const radioButton = option.querySelector(".mbti-choice-input");
    radioButton.checked = false;
  }
}

function checkAllOptionsSelected(radioGroups) {
  const allOptionsSelected =
    radioGroups.length === 4 &&
    radioGroups.every((group) =>
      group.querySelector(".mbti-detail-option.selected")
    );

  const submitButton = document.querySelector(".vote-submit-btn");
  submitButton.disabled = !allOptionsSelected;
}

function checkSubmitButton(radioGroups) {
  const submitButton = document.querySelector(".vote-submit-btn");
  let allSelected = true;

  radioGroups.forEach((group) => {
    const selected = group.querySelector(".mbti-detail-option.selected");
    if (!selected) {
      allSelected = false;
    }
  });

  submitButton.disabled = !allSelected;
}

function updateSelectedMBTI(radioGroups) {
  const selectedMBTISpan = document.getElementById("selected-mbti");
  const selectedMBTIInput = document.getElementById("selected-mbti-input");
  let selectedMBTI = "";

  radioGroups.forEach((group) => {
    const selected = group.querySelector(".mbti-detail-option.selected");
    if (selected) {
      selectedMBTI += selected.querySelector(".mbti-choice-input").value;
    }
  });

  selectedMBTISpan.textContent = selectedMBTI;
  selectedMBTIInput.value = selectedMBTI;
  console.log("Selected MBTI:", selectedMBTI);

  const submitButton = document.querySelector(".vote-submit-btn");
  if (selectedMBTI.length === 4) {
    submitButton.disabled = false;
    submitButton.classList.add("active");
  } else {
    submitButton.disabled = true;
    submitButton.classList.remove("active");
  }
}
