import numpy as np

import county as cty
import facebook_connections as fbc
import plot_counties as pc
import usgeodata as usgd
import usgeodatafactory as ugfac


class GeoConnections:
    def __init__(self, c, s, f):
        self.counties = c
        self.states = s
        self.facebook = f

    def set(self, c, s, f):
        self.counties = c
        self.states = s
        self.facebook = f

    @property
    def values(self):
        return self.counties, self.states, self.facebook


def main():
    the_data = GeoConnections(*get_data(try_cache=True))
    do_repl_loop(the_data)


def get_data(try_cache: bool = True) \
        -> tuple[usgd.UsGeoData, usgd.UsGeoData, fbc.FacebookConnections]:
    fac = ugfac.UsGeoDataFactory()
    states = fac.get("./data/cb_2018_us_state_500k", try_cache)
    counties = fac.get("./data/cb_2018_us_county_500k", try_cache)
    facebook = fbc.FacebookConnections()
    return counties, states, facebook


def do_repl_loop(the_data):
    print("\nProvide the 5 character FPs for the county (2 for state, 3 for county)")
    print("An example for Warren County, OH:")
    print("\t39165")
    print("Reponsd with 'exit' to exit; 'random' for random county; 'refresh' to get uncached data")
    while True:
        response = input("county_id: ").strip().lower()
        if response == "exit":
            break
        elif response == "random":
            random_fips = the_data.counties.get_random_fips()
            try_to_plot_a_county(random_fips, the_data, data_breaks)
        elif response == "refresh":
            the_data.set(*get_data(try_cache=False))
        else:
            try_to_plot_a_county(response, the_data, data_breaks)


def try_to_plot_a_county(candidate_county, the_data, p_data_breaks):
    counties, states, facebook = the_data.values
    try:
        the_county = cty.County(candidate_county, counties)
    except usgd.IndexErrorRegionNotFound:
        print(f"\t[[{candidate_county}]] is a not a valid FIPS")
        return

    counties = assign_color_to_counties_by_facebook_connections(
        counties,
        facebook,
        the_county)
    pc.plot_counties_by_connections_to_the_county(
        the_county,
        states,
        counties,
        p_data_breaks)


def assign_color_to_counties_by_facebook_connections(
        counties: usgd.UsCountiesData,
        facebook: fbc.FacebookConnections,
        the_county: cty.County) -> usgd.UsGeoData:

    counties.assign_values(facebook.get_number_of_connections_from_county(the_county.fips))
    counties.assign_colors(select_color_based_on_percentile(counties, data_breaks))
    counties.assign_color_to_region(the_county.fips, pc.SELECTED_COLOR)

    return counties


data_breaks = [
    (90, pc.DISPLAY_GRADIENT_1, "Top 10%"),
    (70, pc.DISPLAY_GRADIENT_2, "90-70%"),
    (50, pc.DISPLAY_GRADIENT_3, "70-50%"),
    (30, pc.DISPLAY_GRADIENT_4, "50-30%"),
    (0, pc.DISPLAY_GRADIENT_5, "Bottom 30%")
]


def select_color_based_on_percentile(
        counties: usgd.UsCountiesData,
        p_data_breaks: list[tuple]) -> list[str]:

    value_for_percentile = {
        percentile: np.percentile(counties.value, percentile)
        for percentile, _, _ in p_data_breaks
    }

    colors: list[str] = []
    for _, county in counties.iter_all_counties():
        for percentile, color, _ in p_data_breaks:
            if county.value >= value_for_percentile[percentile]:
                colors.append(color)
                break
    return colors


if __name__ == '__main__':
    main()
