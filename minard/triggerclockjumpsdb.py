from .db import engine_test
from .detector_state import get_latest_run

def get_clock_jumps(limit):
    """
    """

    conn = engine_test.connect()

    current_run = get_latest_run()

    result = conn.execute("SELECT DISTINCT ON (run) run "
                          "FROM trigger_clock_jumps WHERE run > %i "
                          "ORDER BY run DESC, timestamp DESC" % (current_run - limit))

    rows = result.fetchall()

    runs = []
    njump10 = {}
    njump50 = {}

    for run in rows:
        runs.append(run[0])
        njump10[run[0]] = 0
        njump50[run[0]] = 0

    result = conn.execute("SELECT DISTINCT ON (run, gtid10, gtid50) "
                          "run, clockjump10, clockjump50 "
                          "FROM trigger_clock_jumps WHERE run > %i "
                          "ORDER BY run DESC, gtid10, gtid50, timestamp DESC" \
                          % (current_run - limit))

    rows = result.fetchall()

    for run, jump10, jump50 in rows:
        if jump10:
            njump10[run] +=1 
        if jump50:
            njump50[run] +=1

    return runs, njump10, njump50

def get_clock_jumps_by_run(run):

    conn = engine_test.connect()

    result = conn.execute("SELECT DISTINCT ON (run, gtid10, gtid50) "
                          "clockjump10, clockfix10, gtid10, "
                          "clockjump50, clockfix50, gtid50 "
                          "FROM trigger_clock_jumps WHERE run = %i "
                          "ORDER BY run DESC, gtid10, gtid50, timestamp DESC" % int(run))

    rows = result.fetchall()

    data10 = []
    data50 = []

    for clockjump10, clockfix10, gtid10, clockjump50, clockfix50, gtid50 in rows:
        if clockjump10:
            # Convert to s for display
            clockjump10 = (clockjump10*100)*1e-9
            # Convert to ns for display
            clockfix10 = (clockfix10)*100*1e-3
            data10.append((clockjump10,clockfix10,gtid10))
        if clockjump50:
            # Convert to s for display
            clockjump50 = (clockjump50*20)*1e-9
            # Convert to us for display
            clockfix50 = (clockfix50)*20*1e-3
            data50.append((clockjump50,clockfix50,gtid50))

    return data10, data50
