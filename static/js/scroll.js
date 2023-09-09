document.addEventListener("DOMContentLoaded", function () {
  const resultContainer = document.querySelector(".result-container");
  if (resultContainer) {
    const blueBgColor = "#f9fcff";
    const purpleBgColor = "#f8f8ff";
    const pinkBgColor = "#fff9f9";
    let currentBgColor = pinkBgColor;

    window.addEventListener("scroll", function () {
      const scrollY = window.scrollY;
      // 스크롤 위치에 따라 배경색 변경
      if (scrollY >= 0 && scrollY < 500) {
        resultContainer.style.backgroundColor = pinkBgColor;
      } else if (scrollY >= 500 && scrollY < 1000) {
        resultContainer.style.backgroundColor = purpleBgColor;
      } else {
        resultContainer.style.backgroundColor = blueBgColor;
      }
    });

    // 초기 배경색 설정
 resultContainer.style.backgroundColor = currentBgColor;
  } else {
    console.error("Element with ID 'capture' not found.");
  }
});