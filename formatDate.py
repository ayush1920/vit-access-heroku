def getDate():
    from datetime import date
    import calendar
    import pytz
    import datetime

    today = date.today()
    day = (calendar.day_name[today.weekday()][:3])
    date = today.strftime("%d %b %Y")
    time = datetime.datetime.now(tz=pytz.utc).strftime(" %H:%M:%S")
    return  day+', '+date+time+' GMT'
