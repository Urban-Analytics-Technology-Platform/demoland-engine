import pandas as pd

import demoland_engine


def test_empty():
    df = demoland_engine.get_empty()
    assert df.shape == (3795, 4)
    assert df.isna().sum().sum() == 15180
    assert df.columns.tolist() == ["signature_type", "use", "greenspace", "job_types"]
    assert df.index.tolist()[:5] == [
        "E00042786",
        "E00042707",
        "E00042703",
        "E00042782",
        "E00042789",
    ]

