from tsm_seg_bkp.bkp_nas_seg import BkpNasSeg


def setup():
    print("SETUP!")


def teardown():
    print("TEAR DOWN!")


def test_file_dont_exists():
    assert BkpNasSeg.config_file_exists('test') != True


def test_file_exists():
    with open('test', mode="w") as local_test:
        pass
    assert BkpNasSeg.config_file_exists('test') == True




