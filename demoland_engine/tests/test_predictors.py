import pandas as pd
import demoland_engine


def test_from_empty():
    demoland_engine.data.change_area("tyne_and_wear")
    df = demoland_engine.get_empty()
    default = demoland_engine.get_indicators(df)
    expected = {
        "air_quality": {
            "count": 3795.0,
            "mean": 15.501793553098024,
            "std": 1.5454279629045733,
            "min": 11.092550486264198,
            "25%": 14.269460278053653,
            "50%": 15.668744754975545,
            "75%": 16.861774346605724,
            "max": 20.69393226702154,
        },
        "house_price": {
            "count": 3795.0,
            "mean": 7.411662620121292,
            "std": 0.2499952158269659,
            "min": 6.574770853715486,
            "25%": 7.2348580566351055,
            "50%": 7.399629173015553,
            "75%": 7.570550702386916,
            "max": 8.263221398536507,
        },
        "job_accessibility": {
            "count": 3795.0,
            "mean": 3505.254281949934,
            "std": 4945.6658986137645,
            "min": 0.0,
            "25%": 1141.0,
            "50%": 2147.0,
            "75%": 4103.5,
            "max": 59468.0,
        },
        "greenspace_accessibility": {
            "count": 3795.0,
            "mean": 480699.6762254817,
            "std": 522631.7770671357,
            "min": 0.0,
            "25%": 159730.13645001693,
            "50%": 300593.8922500339,
            "75%": 598091.1338249899,
            "max": 3452338.444650006,
        },
    }

    pd.testing.assert_frame_equal(pd.DataFrame(expected), default.describe())


def test_from_adapted():
    demoland_engine.data.change_area("tyne_and_wear")
    df = demoland_engine.get_empty()
    df.loc["E00042786"] = [3, 0.4, 0.2, 0.8]
    result = demoland_engine.get_indicators(df, random_seed=0)
    expected = {
        "air_quality": {
            "count": 3795.0,
            "mean": 15.502177806392208,
            "std": 1.5456919105091336,
            "min": 11.092550486264198,
            "25%": 14.269460278053653,
            "50%": 15.668744754975545,
            "75%": 16.861774346605724,
            "max": 20.69393226702154,
        },
        "house_price": {
            "count": 3795.0,
            "mean": 7.411470894282914,
            "std": 0.24996393620953553,
            "min": 6.574770853715486,
            "25%": 7.2348580566351055,
            "50%": 7.399365419939102,
            "75%": 7.56881100526736,
            "max": 8.263221398536507,
        },
        "job_accessibility": {
            "count": 3795.0,
            "mean": 3505.8755210651602,
            "std": 4945.663970174204,
            "min": 0.0,
            "25%": 1141.0,
            "50%": 2147.0,
            "75%": 4103.5,
            "max": 59468.0,
        },
        "greenspace_accessibility": {
            "count": 3795.0,
            "mean": 480797.1864758674,
            "std": 522601.2767654252,
            "min": 0.0,
            "25%": 159730.13645001693,
            "50%": 300593.8922500339,
            "75%": 598091.1338249899,
            "max": 3452338.444650006,
        },
    }

    pd.testing.assert_frame_equal(pd.DataFrame(expected), result.describe())
