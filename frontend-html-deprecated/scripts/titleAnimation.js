/*
 * Dynamic Hero Title Animation
 * Smooth fade transition through different languages
 */

const titleTranslations = [
  { line1: "DISCOVER YOUR", line2: "ALUMNI NETWORK" },      // English
  { line1: "DESCUBRE TU", line2: "RED DE EXALUMNOS" },      // Spanish
  { line1: "DÉCOUVREZ VOTRE", line2: "RÉSEAU D'ANCIENS" },  // French
  { line1: "ENTDECKE DEIN", line2: "ALUMNI-NETZWERK" },     // German
  { line1: "发现你的", line2: "校友网络" },                    // Chinese
  { line1: "अपना खोजें", line2: "पूर्व छात्र नेटवर्क" },      // Hindi
  { line1: "あなたの", line2: "卒業生ネットワーク" },            // Japanese
  { line1: "SCOPRI LA TUA", line2: "RETE DI ALUMNI" },      // Italian
  { line1: "DESCUBRA SUA", line2: "REDE DE ALUMNI" },       // Portuguese
];

let currentTranslationIndex = 0;
let isAnimating = false;

// Initialize with first translation
document.addEventListener('DOMContentLoaded', () => {
  const line1 = document.querySelector('.title-line-1');
  const line2 = document.querySelector('.title-line-2');

  if (line1 && line2) {
    // Set initial text with wrapped letters
    updateLineWithLetters(line1, titleTranslations[0].line1);
    updateLineWithLetters(line2, titleTranslations[0].line2);

    // Start animation cycle after 4 seconds
    setTimeout(startTitleAnimation, 4000);
  }
});

function startTitleAnimation() {
  setInterval(() => {
    if (!isAnimating) {
      animateToNextTranslation();
    }
  }, 6000); // Change every 6 seconds
}

async function animateToNextTranslation() {
  isAnimating = true;

  const line1Element = document.querySelector('.title-line-1');
  const line2Element = document.querySelector('.title-line-2');

  if (!line1Element || !line2Element) return;

  const nextIndex = (currentTranslationIndex + 1) % titleTranslations.length;
  const nextTranslation = titleTranslations[nextIndex];

  // Fade out current text
  await fadeOutLine(line1Element);
  await sleep(100);
  await fadeOutLine(line2Element);

  await sleep(200);

  // Update text
  updateLineWithLetters(line1Element, nextTranslation.line1);
  updateLineWithLetters(line2Element, nextTranslation.line2);

  await sleep(100);

  // Fade in new text
  await fadeInLine(line1Element);
  await sleep(100);
  await fadeInLine(line2Element);

  currentTranslationIndex = nextIndex;
  isAnimating = false;
}

function updateLineWithLetters(element, text) {
  element.innerHTML = '';
  const letters = text.split('');

  letters.forEach((char, index) => {
    const span = document.createElement('span');
    span.className = 'letter';
    span.textContent = char === ' ' ? '\u00A0' : char;
    span.style.transitionDelay = `${index * 20}ms`;
    element.appendChild(span);
  });
}

async function fadeOutLine(element) {
  const letters = element.querySelectorAll('.letter');
  letters.forEach((letter, index) => {
    setTimeout(() => {
      letter.style.opacity = '0';
      letter.style.transform = 'translateY(20px) scale(0.8)';
      letter.style.filter = 'blur(4px)';
    }, index * 20);
  });

  await sleep(letters.length * 20 + 300);
}

async function fadeInLine(element) {
  const letters = element.querySelectorAll('.letter');
  letters.forEach((letter, index) => {
    letter.style.opacity = '0';
    letter.style.transform = 'translateY(-20px) scale(0.8)';
    letter.style.filter = 'blur(4px)';

    setTimeout(() => {
      letter.style.opacity = '1';
      letter.style.transform = 'translateY(0) scale(1)';
      letter.style.filter = 'blur(0px)';
    }, index * 20);
  });

  await sleep(letters.length * 20 + 300);
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Pause animation on hover
const heroTitle = document.getElementById('dynamicTitle');
if (heroTitle) {
  heroTitle.addEventListener('mouseenter', () => {
    isAnimating = true;
  });

  heroTitle.addEventListener('mouseleave', () => {
    setTimeout(() => {
      isAnimating = false;
    }, 1000);
  });
}
