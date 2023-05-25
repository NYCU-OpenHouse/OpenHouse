// // Grab wrapper nodes
const rootNode = document.querySelector('.embla')
const viewportNode = rootNode.querySelector('.embla__viewport')

// Grab button nodes
const prevButtonNode = rootNode.querySelector('.embla__button--prev')
const nextButtonNode = rootNode.querySelector('.embla__button--next')
const dotsNode = rootNode.querySelector('.embla__dots')

// Initialize the carousel
// const autoplayOptions = {
//   delay: 4000,
//   rootNode: (emblaRoot) => emblaRoot.parentElement,
// }
var options = { loop: true }
const embla = EmblaCarousel(viewportNode, options, [EmblaCarouselAutoplay()])

// Add click listeners
prevButtonNode.addEventListener('click', embla.scrollPrev, false)
nextButtonNode.addEventListener('click', embla.scrollNext, false)
const addDotBtnsAndClickHandlers = (emblaApi, dotsNode) => {
  let dotNodes = []

  const addDotBtnsWithClickHandlers = () => {
    dotsNode.innerHTML = emblaApi
      .scrollSnapList()
      .map(() => '<button class="embla__dot" type="button"></button>')
      .join('')

    dotNodes = Array.from(dotsNode.querySelectorAll('.embla__dot'))
    dotNodes.forEach((dotNode, index) => {
      dotNode.addEventListener('click', () => emblaApi.scrollTo(index), false)
    })
  }

  const toggleDotBtnsActive = () => {
    const previous = emblaApi.previousScrollSnap()
    const selected = emblaApi.selectedScrollSnap()
    dotNodes[previous].classList.remove('embla__dot--selected')
    dotNodes[selected].classList.add('embla__dot--selected')
  }

  emblaApi
    .on('init', addDotBtnsWithClickHandlers)
    .on('reInit', addDotBtnsWithClickHandlers)
    .on('init', toggleDotBtnsActive)
    .on('reInit', toggleDotBtnsActive)
    .on('select', toggleDotBtnsActive)

  return () => {
    dotsNode.innerHTML = ''
  }
}
const removeDotBtnsAndClickHandlers = addDotBtnsAndClickHandlers(
  embla,
  dotsNode,
);
embla.on('destroy', removeDotBtnsAndClickHandlers)