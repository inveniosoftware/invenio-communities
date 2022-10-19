/*
 * This file is part of Invenio.
 * Copyright (C) 2016-2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React, { Component } from "react";
import PropTypes from "prop-types";
import _truncate from "lodash/truncate";
import { i18next } from "@translations/invenio_communities/i18next";
import { http } from "../../api/config";
import { withCancel } from "react-invenio-forms";
import { Transition, Container, Grid, Header, Item, Icon } from "semantic-ui-react";
import CarouselItem from "./CarouselItem";

export default class CommunitiesCarousel extends Component {
  constructor(props) {
    super(props);

    this.state = {
      isLoading: false,
      data: { hits: [] },
      error: {},
      activeIndex: 0,
      animationDirection: 'left',
      carouselTimer: null,
    };
  }

  getDataIndex = (index) => {
    const { data: { hits }} = this.state;
    if(index > hits.length - 1) return 0;
    if(index < 0) return hits.length - 1;
    return index;
  }

  runCarousel = async (newIndex) => {
    const { activeIndex } = this.state;
    let animationDirection = newIndex < activeIndex ? 'right' : 'left';
    await this.setState({ animationDirection });
    this.setState({ activeIndex: this.getDataIndex(newIndex) })
  }

  setCarouselTimer = () => {
    const { data } = this.state;
    const { intervalDelay } = this.props;
    this.setState({
      carouselTimer: setInterval(() => {
        data.hits.length && this.runCarousel(this.state.activeIndex + 1);
      }, intervalDelay)
    })
  }

  // Pause carousel when user focuses elements in the container
  stopCarousel = () => { clearInterval(this.state.carouselTimer) }
  startCarousel = () => { this.setCarouselTimer() }

  componentWillUnmount() {
    this.cancellableFetch && this.cancellableFetch.cancel();
    this.stopCarousel();
  }

  componentDidMount() {
    this.fetchData();
  }

  fetchData = async () => {
    this.setState({ isLoading: true });
    this.cancellableFetch = withCancel(http.get(this.props.fetchUrl));

    try {
      const response = await this.cancellableFetch.promise;
      this.setState({ data: response.data.hits, isLoading: false });
      this.setCarouselTimer();
    } catch (error) {
      console.error(error);
    }
  };

  render() {
    const { data, animationDirection, activeIndex } = this.state;
    const { title, animationSpeed, defaultLogo } = this.props;

    const carouselSlides = data.hits?.map(
      (community, index) => (
        index === activeIndex && (
          <CarouselItem community={community} defaultLogo={defaultLogo} key={community.id} />
        )
      )
    );

    return data.hits.length ? (
      <Container fluid className="carousel rel-pt-2 rel-pb-2 ml-0-mobile mr-0-mobile">
        {title && (
          <Container className="rel-mb-1">
            <Header as="h2">{title}</Header>
          </Container>
        )}

        <Grid
          container
          onFocus={this.stopCarousel}
          onBlur={this.startCarousel}
        >
          <Grid.Column
            width="2"
            className="pr-0"
            verticalAlign="middle"
            textAlign="left"
          >
            <Icon
              className="carousel-arrow"
              inverted
              role="button"
              name="angle left"
              size="huge"
              aria-label={i18next.t("Previous slide")}
              onClick={() => this.runCarousel(activeIndex - 1)}
              onKeyDown={(event) => event.key === "Enter" && this.runCarousel(activeIndex - 1)}
              tabIndex="0"
            />
          </Grid.Column>

          <Grid.Column width="12" className="flex align-items-center">
            <Transition.Group
              as={Item.Group}
              className="flex align-items-center justify-center"
              duration={animationSpeed}
              animation={`carousel-slide ${animationDirection}`}
              directional={true}
            >
              {carouselSlides}
            </Transition.Group>
          </Grid.Column>

          <Grid.Column
            width="2"
            className="pl-0"
            verticalAlign="middle"
            textAlign="right"
          >
            <Icon
              className="carousel-arrow"
              inverted
              role="button"
              name="angle right"
              size="huge"
              aria-label={i18next.t("Next slide")}
              onClick={() => this.runCarousel(activeIndex + 1)}
              onKeyDown={(event) => event.key === "Enter" && this.runCarousel(activeIndex + 1)}
              tabIndex="0"
            />
          </Grid.Column>
        </Grid>
      </Container>
    ) : "";
  }
}

CommunitiesCarousel.propTypes = {
  title: PropTypes.string.isRequired,
  fetchUrl: PropTypes.string.isRequired,
  intervalDelay: PropTypes.number.isRequired,
  animationSpeed: PropTypes.number.isRequired,
  defaultLogo: PropTypes.string.isRequired,
};
