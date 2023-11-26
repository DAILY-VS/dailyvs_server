const target1 = {{ choice1_percentage }};
const target2 = {{ choice2_percentage }};
const percentage1Element = document.getElementById("percentage1");
const percentage2Element = document.getElementById("percentage2");
const duration = 2500;

const animatePercentage = (element, target) => {
  let current = 0;
  const increment = target / (duration / 10);

  const interval = setInterval(() => {
    current += increment;
    element.textContent = `${Math.min(Math.round(current), target)}%`;
    const colorValue = Math.round((current / target) * 255);
    element.style.color = `rgb(${colorValue}, ${255 - colorValue}, 0)`;
    if (current >= target) {
      clearInterval(interval);
    }
  }, 10);
};

animatePercentage(percentage1Element, target1);
animatePercentage(percentage2Element, target2);