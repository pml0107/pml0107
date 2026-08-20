from __future__ import annotations

from generate_ascii import DEFAULT_INPUT as ASCII_INPUT
from generate_ascii import DEFAULT_OUTPUT as ASCII_OUTPUT
from generate_ascii import image_to_ascii, render_ascii_svg
from generate_contributions import render_heatmap
from generate_info_card import render_info_card
from prepare_photo import DEFAULT_INPUT as PHOTO_INPUT
from prepare_photo import DEFAULT_OUTPUT as PHOTO_OUTPUT
from prepare_photo import prepare_photo
from svg_utils import ASSETS, DATA


def main() -> None:
    prepare_photo(PHOTO_INPUT, PHOTO_OUTPUT)
    render_ascii_svg(image_to_ascii(ASCII_INPUT), ASCII_OUTPUT)
    render_info_card(ASSETS / "info-card.svg")
    render_heatmap(DATA / "contributions.json", ASSETS / "contribution-graph.svg")


if __name__ == "__main__":
    main()

