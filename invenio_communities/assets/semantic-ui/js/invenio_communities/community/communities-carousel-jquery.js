/*
 * This file is part of Invenio.
 * Copyright (C) 2023 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import $ from "jquery";

$(() => {
  const communitiesCarouselContainer = document.getElementById(
    "communities-carousel-jquery"
  );
  const intervalDelay = parseInt(communitiesCarouselContainer.dataset.intervalDelay);
  const animationSpeed = parseInt(communitiesCarouselContainer.dataset.animationSpeed);

  const carouselSlides = $("#carousel-slides").find(".carousel.transition");
  const prevSlideBtn = $("#prev-slide-btn");
  const nextSlideBtn = $("#next-slide-btn");

  const minIndex = 0;
  const maxIndex = carouselSlides.length - 1;
  var activeIndex = 0;

  /**
   * Switches carousel slide
   * @param {string} direction Direction to slide - left or right
   */
  const slide = (direction) => {
    const prevIndex = activeIndex;

    if (direction === "left") {
      activeIndex++;
      if (activeIndex > maxIndex) activeIndex = 0;
    } else {
      activeIndex--;
      if (activeIndex < minIndex) activeIndex = maxIndex;
    }

    $(carouselSlides[activeIndex]).transition({
      animation: `carousel-slide ${direction} in`,
      duration: animationSpeed,
    });

    $(carouselSlides[prevIndex]).transition({
      animation: `carousel-slide ${direction} out`,
      duration: animationSpeed,
    });
  };

  // Run carousel automatically on page load
  const setCarouselTimer = () => setInterval(() => slide("left"), intervalDelay);
  var carouselTimer = setCarouselTimer();

  // Pause carousel on focus
  $(communitiesCarouselContainer)
    .on("focusin", () => {
      clearInterval(carouselTimer);
    })
    .on("focusout", () => {
      carouselTimer = setCarouselTimer();
    });

  // Navigation arrow event handlers
  prevSlideBtn
    .on("click", () => slide("right"))
    .on("keydown", (event) => {
      event.key === "Enter" && slide("right");
    });
  nextSlideBtn
    .on("click", () => slide("left"))
    .on("keydown", (event) => {
      event.key === "Enter" && slide("left");
    });
});
