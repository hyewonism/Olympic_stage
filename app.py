import re
from datetime import datetime

import mysql.connector
from mysql.connector import FieldType
from flask import Flask, render_template, request, redirect, url_for

import connect

app = Flask(__name__)

connection = mysql.connector.connect(
    user=connect.dbuser,
    password=connect.dbpass,
    host=connect.dbhost,
    database=connect.dbname,
    autocommit=True,
)
dbconn = connection.cursor()


@app.route("/")
def home():
    return render_template("base.html")


@app.route("/listmembers")
def listmembers():
    dbconn.execute(
        """
        SELECT memberid, teamname, CONCAT(firstname, ' ', lastname) AS name, city, birthdate
        FROM members
        JOIN teams ON members.teamid = teams.teamid;
        """
    )
    memberList = dbconn.fetchall()
    print(memberList)
    return render_template("memberlist.html", memberlist=memberList)


@app.route("/listevents")
def listevents():
    dbconn.execute("SELECT * FROM events;")
    eventList = dbconn.fetchall()
    return render_template("eventlist.html", eventlist=eventList)


@app.route("/athlete")
def athelete():
    """
    http://127.0.0.1:5000/athlete?memberid=5632
    """
    memberName = request.args.get('memberName')

    dbconn.execute(
        """
        SELECT e.sport, e.EventName, es.location, es.stagename, esr.position, es.stagedate
        FROM event_stage_results as esr
        JOIN event_stage as es ON esr.StageID = es.StageID
        JOIN events as e ON es.EventID = e.EventID
        WHERE CONCAT(esr.firstname, ' ', esr.lastname) = %s;
        """,
        (memberName,),
    )
    events = dbconn.fetchall()
    upcomingEvents = {}
    pastEvents = {}
    for event in events:
        if event[4] is None:
            if event[0] not in upcomingEvents:
                upcomingEvents[event[0]] = []
            upcomingEvents[event[0]].append(event)
        else:
            if event[0] not in pastEvents:
                pastEvents[event[0]] = []
            pastEvents[event[0]].append(event)

    print(upcomingEvents, pastEvents)

    return render_template(
        "athlete.html",
        upcomingEvents=upcomingEvents.values(),
        pastEvents=pastEvents.values(),
    )


@app.route("/admin/search", methods=["GET", "POST"])
def admin_search():
    """
    A search that searches either/or both of members and events using partial matches. o Add new members and edit the details of existing members.
    """
    if request.method == "POST":
        search = request.form.get("search")
        print(search)
        dbconn.execute(
            """
            SELECT memberid, teamname, CONCAT(firstname, ' ', lastname) AS name, city, birthdate
            FROM members
            JOIN teams ON members.teamid = teams.teamid
            WHERE CONCAT(firstname, ' ', lastname) LIKE %s;
            """,
            (f"%{search}%",),
        )
        memberList = dbconn.fetchall()
        print(memberList)
        dbconn.execute(
            """
            SELECT * FROM events
            WHERE EventName LIKE %s;
            """,
            (f"%{search}%",),
        )
        eventList = dbconn.fetchall()
        print(eventList)

        return render_template(
            "adminsearch.html", memberlist=memberList, eventlist=eventList
        )
    else:
        return render_template("adminsearch.html")


@app.route("/admin/member", methods=["GET", "POST"])
def admin_member():
    """
    A search that searches either/or both of members and events using partial matches. o Add new members and edit the details of existing members.
    """
    if request.method == "POST":
        memberid = request.form.get("memberid")
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        city = request.form.get("city")
        birthdate = request.form.get("birthdate")
        teamid = request.form.get("teamid")
        print(memberid, firstname, lastname, city, birthdate, teamid)
        dbconn.execute(
            """
            UPDATE members
            SET firstname = %s, lastname = %s, city = %s, birthdate = %s, teamid = %s
            WHERE memberid = %s;
            """,
            (firstname, lastname, city, birthdate, teamid, memberid),
        )
        return redirect(url_for("listmembers"))
    else:
        memberid = request.args.get("memberid")
        dbconn.execute(
            """
            SELECT memberid, firstname, lastname, city, birthdate, teamid
            FROM members
            WHERE memberid = %s;
            """,
            (memberid,),
        )
        member = dbconn.fetchone()
        print(member)
        dbconn.execute(
            """
            SELECT teamid, teamname
            FROM teams;
            """
        )
        teams = dbconn.fetchall()
        print(teams)
        return render_template("adminmember.html", member=member, teams=teams)


@app.route("/admin/event", methods=["GET", "POST"])
def admin_event():
    if request.method == "POST":
        sport = request.form.get("sportid")
        teamid = request.form.get("teamid")
        eventid = request.form.get("eventid")
        dbconn.execute(
            """
            UPDATE events
            SET sport = %s, NZTeam = %s
            WHERE eventid = %s;
            """,
            (sport, teamid, eventid),
        )
        return redirect(url_for("listevents"))
    else:
        dbconn.execute(
            """
            SELECT eventid, eventname
            FROM events
            """,
        )
        events = dbconn.fetchall()

        # fetch sport and teamid list
        dbconn.execute(
            """
            SELECT sport
            FROM events;
            """
        )
        sports = set([sport for sport in dbconn.fetchall()])
        print(sports)

        dbconn.execute(
            """
            SELECT NZTeam
            FROM events;
            """
        )
        teams = set([team for team in dbconn.fetchall()])
        print(teams)

        return render_template(
            "adminevent.html", events=events, sports=sports, teams=teams
        )


@app.route("/admin/eventstage", methods=["GET", "POST"])
def admin_eventstage():
    """
    Add scores for an event stage and position for a non-qualifying event stage.
    """
    if request.method == "POST":
        eventid = request.form.get("eventid")
        stagename = request.form.get("stagename")
        location = request.form.get("location")
        stagedate = request.form.get("stagedate")
        print(eventid, stagename, location, stagedate)
        dbconn.execute(
            """
            UPDATE event_stage
            SET stagename = %s, location = %s, stagedate = %s
            WHERE eventid = %s
            """,
            (stagename, location, stagedate, eventid),
        )
        return redirect(url_for("listevents"))
    else:
        dbconn.execute(
            """
            SELECT eventid, stagename, location, stagedate
            FROM event_stage
            WHERE Qualifying = 0;
            """
        )
        event_stages = dbconn.fetchall()
        event_ids = sorted(set([event[0] for event in event_stages]))
        stage_names = set([event[1] for event in event_stages])
        locations = set([event[2] for event in event_stages])

        return render_template(
            "admineventstage.html",
            event_ids=event_ids,
            stage_names=stage_names,
            locations=locations,
        )


@app.route("/admin/position")
def admin_position():
    """
    Show the following reports
    ▪ Number of Gold, Silver and Bronze Medals and who has won them.
    """

    dbconn.execute(
        """
        SELECT *
        FROM event_stage_results
        WHERE position IS NOT NULL;
        """
    )

    results = dbconn.fetchall()
    print(results)
    # find positions for each stage. First position is gold, second is silver, third is bronze

    positions = {
        "Gold": [],
        "Silver": [],
        "Bronze": [],
    }
    for result in results:
        if result[4] == 1:
            positions["Gold"].append(result)
        elif result[4] == 2:
            positions["Silver"].append(result)
        elif result[4] == 3:
            positions["Bronze"].append(result)

    print(positions)

    return render_template(
        "adminposition.html",
        gold=positions["Gold"],
        silver=positions["Silver"],
        bronze=positions["Bronze"],
    )


app.run(debug=True)
