import random
from datetime import datetime
import pandas as pd
from fastapi.responses import FileResponse
from fastapi.responses import RedirectResponse
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, text
from starlette.middleware.sessions import SessionMiddleware
from fastapi import Form
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from fastapi.responses import RedirectResponse

from reportlab.lib import colors
app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key="vehiclehealth123"
)

templates = Jinja2Templates(directory="templates")

DATABASE_URL = "sqlite:///vehicle.db"
engine = create_engine(DATABASE_URL)

class Vehicle(BaseModel):
    vehicle_id: str
    speed: int
    engine_temp: int
    fuel_level: int
    battery_voltage: float

@app.get("/")
def root():
    return RedirectResponse(
        url="/login",
        status_code=303
    )

    with engine.connect() as conn:

        total = conn.execute(
            text("SELECT COUNT(*) FROM vehicle")
        ).scalar()

        healthy = conn.execute(
            text("SELECT COUNT(*) FROM vehicle WHERE status='Healthy'")
        ).scalar()

        critical = conn.execute(
            text("SELECT COUNT(*) FROM vehicle WHERE status='Critical'")
        ).scalar()

        result = conn.execute(
            text("SELECT * FROM vehicle")
        )

        table_rows = ""

        for row in result:

            table_rows += f"""
            <tr>
                <td>{row[1]}</td>
                <td>{row[2]}</td>
                <td>{row[3]}</td>
                <td>{row[4]}</td>
                <td>{row[5]}</td>
                <td>{row[6]}</td>
                
            </tr>
            """

    return f"""
    <!DOCTYPE html>
    <html>

    <head>
        <title>Vehicle Dashboard</title>
    </head>

    <body>

        <h1>🚗 Vehicle Health Monitoring Dashboard</h1>

        <h2>Total Vehicles: {total}</h2>
        <h2>Healthy Vehicles: {healthy}</h2>
        <h2>Critical Vehicles: {critical}</h2>

        <h2>Vehicle Records</h2>

        <table border="1">

            <tr>
                <th>Vehicle ID</th>
                <th>Speed</th>
                <th>Temperature</th>
                <th>Fuel</th>
                <th>Battery</th>
                <th>Status</th>
                <th>DTC Code</th>
                <th>DTC Description</th>
            </tr>

            {table_rows}

        </table>

        <br><br>

        <a href="/docs">Swagger UI</a>

    </body>

    </html>
    """
from fastapi.responses import HTMLResponse

@app.get("/add-vehicle", response_class=HTMLResponse)
def add_vehicle_page():

    return """
    <html>
    <body>

        <h1>Add Vehicle</h1>

        <form action="/save-vehicle" method="post">

            Vehicle ID:
            <input type="text" name="vehicle_id">

            <br><br>

            Speed:
            <input type="number" name="speed">

            <br><br>

            Temperature:
            <input type="number" name="engine_temp">

            <br><br>

            Fuel:
            <input type="number" name="fuel_level">

            <br><br>

            Battery:
            <input type="number" step="0.1" name="battery_voltage">

            <button>
            Save Vehicle
            </button>

        </form>

    </body>
    </html>
    """
@app.post("/save-vehicle")
def save_vehicle(
    vehicle_id: str = Form(...),
    speed: int = Form(...),
    engine_temp: int = Form(...),
    fuel_level: int = Form(...),
    battery_voltage: float = Form(...)
):

    status = "Healthy"

    if engine_temp > 100:
        status = "Critical"

    elif fuel_level < 15:
        status = "Warning"

    elif battery_voltage < 11:
        status = "Critical"

    with engine.connect() as conn:

        conn.execute(
            text("""
            INSERT INTO vehicle
            (vehicle_id, speed, engine_temp, fuel_level, battery_voltage, status)
            VALUES
            (:vehicle_id, :speed, :engine_temp, :fuel_level, :battery_voltage, :status)
            """),
            {
                "vehicle_id": vehicle_id,
                "speed": speed,
                "engine_temp": engine_temp,
                "fuel_level": fuel_level,
                "battery_voltage": battery_voltage,
                "status": status
            }
        )

        conn.commit()
        return RedirectResponse(
            url="/",
            status_code=303
        )

   
@app.post("/vehicle")
def add_vehicle(vehicle: Vehicle):

    status = "Healthy"
    dtc_code = ""

    dtc_description = ""

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if vehicle.engine_temp > 100:
        status = "Critical"

    elif vehicle.fuel_level < 15:
        status = "Warning"

    elif vehicle.battery_voltage < 11:
        status = "Critical"

    with engine.connect() as conn:

        conn.execute(
            text("""
            INSERT INTO vehicle
            (vehicle_id, speed, engine_temp, fuel_level, battery_voltage, status,dtc_code, dtc_description)
            VALUES
            (:vehicle_id, :speed, :engine_temp, :fuel_level, :battery_voltage, :status,:dtc_code, :dtc_description)
            """),
            {
                "vehicle_id": vehicle.vehicle_id,
                "speed": vehicle.speed,
                "engine_temp": vehicle.engine_temp,
                "fuel_level": vehicle.fuel_level,
                "battery_voltage": vehicle.battery_voltage,
                "status": status,
                "dtc_code": dtc_code,
                "dtc_description": dtc_description


            }
        )

        conn.commit()

    return {
        "message": "Vehicle Added Successfully",
        "status": status
    }

@app.get("/vehicles")
def get_vehicles():

    with engine.connect() as conn:

        result = conn.execute(
            text("SELECT * FROM vehicle")
        )

        vehicles = []

        for row in result:
            risk_score = 0

            if row[3] > 100:      # engine_temp
                risk_score += 40

            if row[4] < 15:       # fuel_level
                risk_score += 30

            if row[5] < 11:       # battery_voltage
                risk_score += 30

            vehicles.append({
                "id": row[0],
                "vehicle_id": row[1],
                "speed": row[2],
                "engine_temp": row[3],
                "fuel_level": row[4],
                "battery_voltage": row[5],
                "status": row[6],
                "dtc_code": row[7],
                "dtc_description": row[8],
                "risk_score": risk_score
            })

    return vehicles 

@app.get("/report/{vehicle_id}")
def generate_report(
    request: Request,
    vehicle_id: int
):
 if "user" not in request.session:

   return {
    "message": "Vehicle Saved Successfully",
    "status": status
}

 def generate_report(vehicle_id: int):

    with engine.connect() as conn:

        result = conn.execute(
            text("SELECT * FROM vehicle WHERE id=:id"),
            {"id": vehicle_id}
        )

        vehicle = result.fetchone()

    pdf_file = f"vehicle_report_{vehicle_id}.pdf"

    doc = SimpleDocTemplate(pdf_file)

    styles = getSampleStyleSheet()

    content = []

    # Header

    title_table = Table(
        [["VEHICLE HEALTH REPORT"]],
        colWidths=[500]
    )

    title_table.setStyle(
        TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.darkblue),
            ('TEXTCOLOR', (0,0), (-1,-1), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTSIZE', (0,0), (-1,-1), 18),
            ('BOTTOMPADDING', (0,0), (-1,-1), 12)
        ])
    )

    content.append(title_table)

    content.append(Spacer(1,20))

    # Status Color

    if vehicle[6] == "Healthy":

        status_color = colors.green

    elif vehicle[6] == "Warning":

        status_color = colors.orange

    else:

        status_color = colors.red

    # Vehicle Info Table

    vehicle_table = Table([
        ["Vehicle ID", vehicle[1]],
        ["Speed", f"{vehicle[2]} km/h"],
        ["Engine Temp", f"{vehicle[3]} °C"],
        ["Fuel Level", f"{vehicle[4]} %"],
        ["Battery Voltage", f"{vehicle[5]} V"]
    ])

    vehicle_table.setStyle(
        TableStyle([
            ('GRID',(0,0),(-1,-1),1,colors.black),
            ('BACKGROUND',(0,0),(0,-1),colors.lightgrey)
        ])
    )

    content.append(
        Paragraph(
            "<b>Vehicle Information</b>",
            styles["Heading2"]
        )
    )

    content.append(vehicle_table)

    content.append(Spacer(1,15))

    # Status Table

    status_table = Table([
        ["Status", vehicle[6]]
    ])

    status_table.setStyle(
        TableStyle([
            ('GRID',(0,0),(-1,-1),1,colors.black),
            ('BACKGROUND',(1,0),(1,0),status_color),
            ('TEXTCOLOR',(1,0),(1,0),colors.white)
        ])
    )

    content.append(
        Paragraph(
            "<b>Vehicle Status</b>",
            styles["Heading2"]
        )
    )

    content.append(status_table)

    content.append(Spacer(1,15))

    risk_score = 0

    if vehicle[3] > 100:
        risk_score += 40

    if vehicle[4] < 15:
        risk_score += 30

    if vehicle[5] < 11:
        risk_score += 30

    if risk_score >= 70:

        recommendation = "Service Immediately"
        risk_color = colors.red

    elif risk_score >= 40:

        recommendation = "Schedule Maintenance"
        risk_color = colors.orange

    else:

        recommendation = "Vehicle Healthy"
        risk_color = colors.green

    risk_table = Table([
        ["Risk Score", f"{risk_score}%"],
        ["Recommendation", recommendation]
    ])

    risk_table.setStyle(
        TableStyle([
            ('GRID',(0,0),(-1,-1),1,colors.black),
            ('BACKGROUND',(1,0),(1,0),risk_color),
            ('TEXTCOLOR',(1,0),(1,0),colors.white)
        ])
    )

    content.append(
        Paragraph(
            "<b>Predictive Maintenance</b>",
            styles["Heading2"]
        )
    )

    content.append(risk_table)

    content.append(Spacer(1,15))

    dtc_table = Table([
    ["DTC Code", str(vehicle[7])],
    ["Description", str(vehicle[8])]
])

    dtc_table.setStyle(
        TableStyle([
            ('GRID',(0,0),(-1,-1),1,colors.black),
            ('BACKGROUND',(0,0),(0,-1),colors.lightgrey)
        ])
    )

    content.append(
        Paragraph(
            "<b>DTC Information</b>",
            styles["Heading2"]
        )
    )

    content.append(dtc_table)
        
    doc.build(content)

    return FileResponse(
            pdf_file,
            media_type="application/pdf",
            filename=pdf_file
        )

@app.get("/login")
def login_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="login.html"
    )
@app.post("/login")
def login(

    request: Request,
    username: str = Form(...),
    password: str = Form(...)

):
    print("USERNAME =", username)
    print("PASSWORD =", password)

    if username == "admin" and password == "admin123":

        request.session["user"] = username

        return RedirectResponse(
            url="/dashboard",
            status_code=303
        )

    return RedirectResponse(
        url="/login",
        status_code=303
    )
@app.get("/logout")
def logout(request: Request):

    request.session.clear()

    return RedirectResponse(
        url="/login",
        status_code=303
    )
@app.get("/vehicle/{vehicle_id}")
def view_vehicle(
    request: Request,
    vehicle_id: int
):
    if "user" not in request.session:

        return RedirectResponse(
            url="/login",
            status_code=303
        )

    with engine.connect() as conn:

        result = conn.execute(
            text("SELECT * FROM vehicle WHERE id=:id"),
            {"id": vehicle_id}
        )

        vehicle = result.fetchone()
    risk_score = 0

    if vehicle[3] > 100:
        risk_score += 40

    if vehicle[4] < 15:
        risk_score += 30

    if vehicle[5] < 11:
        risk_score += 30

    if risk_score >= 70:

        recommendation = "Service Immediately"

    elif risk_score >= 40:

        recommendation = "Schedule Maintenance"

    else:

        recommendation = "Vehicle Healthy"

    return templates.TemplateResponse(
        request=request,
        name="vehicle_details.html",
        context={
            "request": request,
            "vehicle": vehicle,
            "risk_score": risk_score,
            "recommendation": recommendation
        }
    )


@app.get("/dashboard")
#def dashboard(request: Request):
def dashboard(
    request: Request,
    search: str = "",
    status: str = ""
):   
    if "user" not in request.session:

     return RedirectResponse(
        url="/login",
        status_code=303
    )

    with engine.connect() as conn:
        total = conn.execute(
           text("SELECT COUNT(*) FROM vehicle")
        ).scalar()

        healthy = conn.execute(
          text("SELECT COUNT(*) FROM vehicle WHERE status='Healthy'")
        ).scalar()

        critical = conn.execute(
          text("SELECT COUNT(*) FROM vehicle WHERE status='Critical'")
        ).scalar()

        warning = conn.execute(
          text("SELECT COUNT(*) FROM vehicle WHERE status='Warning'")
        ).scalar()

        trend_result = conn.execute(
            text("""
            SELECT
                substr(created_at,1,13) as hour,
                COUNT(*) as total
            FROM vehicle
            WHERE created_at IS NOT NULL
            GROUP BY hour
            ORDER BY hour
            """)
            )

        trend_labels = []
        trend_data = []

        for row in trend_result:
            trend_labels.append(row[0])
            trend_data.append(row[1])

        health_trend = conn.execute(
           text("""
           SELECT
              substr(created_at,1,13) as hour,

            SUM(
                CASE
                    WHEN status='Healthy'
                    THEN 1
                    ELSE 0
                END
            ) as healthy,

            SUM(
                CASE
                    WHEN status='Critical'
                    THEN 1
                    ELSE 0
                END
            ) as critical,

            SUM(
                CASE
                    WHEN status='Warning'
                    THEN 1
                    ELSE 0
                END
            ) as warning

            FROM vehicle

            WHERE created_at IS NOT NULL

            GROUP BY hour

            ORDER BY hour
            """)
        )

        health_labels = []

        healthy_data = []

        critical_data = []

        warning_data = []

        for row in health_trend:

            health_labels.append(row[0])

            healthy_data.append(row[1])

            critical_data.append(row[2])

            warning_data.append(row[3])

            print("LABELS =", health_labels)
            print("HEALTHY =", healthy_data)
            print("CRITICAL =", critical_data)
            print("WARNING =", warning_data)

        if search:

          result = conn.execute(
               text("""
                    SELECT * FROM vehicle
                    WHERE vehicle_id LIKE :search
                    """),
                    {
                        "search": f"%{search}%"
                     }
                )

        elif status:

            result = conn.execute(
            text("""
            SELECT * FROM vehicle
            WHERE status = :status
            """),
            {
                "status": status
            }
        )

        else:

            result = conn.execute(
        text("SELECT * FROM vehicle")
        )
            
    vehicles = []
       
    for row in result:
            risk_score = 0

            if row[3] > 100:
                risk_score += 40

            if row[4] < 15:
                risk_score += 30

            if row[5] < 11:
                risk_score += 30
            vehicles.append({
                "id": row[0],
                "vehicle_id": row[1],
                "speed": row[2],
                "engine_temp": row[3],
                "fuel_level": row[4],
                "battery_voltage": row[5],
                "status": row[6],
                "dtc_code": row[7],
                "dtc_description": row[8],
                "created_at": row[9], 
                "risk_score": risk_score
                
            })
        
    alerts = []
    maintenance_alerts = []

    for vehicle in vehicles:

            if vehicle["engine_temp"] > 100:
                alerts.append(
                f"🔥 {vehicle['vehicle_id']} - High Engine Temperature"
                )

            if vehicle["fuel_level"] < 15:
                alerts.append(
                f"⛽ {vehicle['vehicle_id']} - Low Fuel Level"
            )

            if vehicle["battery_voltage"] < 11:
                alerts.append(
                f"🔋 {vehicle['vehicle_id']} - Low Battery Voltage"
            )
            
            if vehicle["risk_score"] >= 70:

              maintenance_alerts.append(
                 f"🔧 {vehicle['vehicle_id']} - Service Immediately"
                )

            elif vehicle["risk_score"] >= 40:

               maintenance_alerts.append(
                 f"🛠️ {vehicle['vehicle_id']} - Schedule Maintenance"
                )
               
    return templates.TemplateResponse(
    request=request,
    name="dashboard.html",
    context={
        
        "vehicles": vehicles,
        "total": total,
        "healthy": healthy,
        "critical": critical,
        "warning": warning,
        "alerts": alerts,
        "user": request.session["user"],
        "trend_labels": trend_labels,
        "trend_data": trend_data,
        "health_labels": health_labels,
        "healthy_data": healthy_data,
        "critical_data": critical_data,
        "warning_data": warning_data,
        "risk_score": risk_score,
        "maintenance_alerts": maintenance_alerts
    }
)

@app.get("/export")
def export_excel():

    with engine.connect() as conn:

        result = conn.execute(
            text("SELECT * FROM vehicle")
        )

        vehicles = []

        for row in result:
            vehicles.append({
                "ID": row[0],
                "Vehicle ID": row[1],
                "Speed": row[2],
                "Engine Temp": row[3],
                "Fuel Level": row[4],
                "Battery Voltage": row[5],
                "Status": row[6],
                "dtc_code": row[7],
                "dtc_description": row[8],
                "created_at": row[9],
                #"risk_score": risk_score
            })

    df = pd.DataFrame(vehicles)

    df.to_excel(
        "vehicles.xlsx",
        index=False
    )

    return FileResponse(
        "vehicles.xlsx",
        filename="vehicles.xlsx"
    )

@app.get("/stats")
def stats():

    with engine.connect() as conn:

        result = conn.execute(
            text("SELECT COUNT(*) FROM vehicle")
        )

        total = result.scalar()

    return {
        "total_vehicles": total
    }

@app.get("/health-stats")
def health_stats():

    with engine.connect() as conn:

        healthy = conn.execute(
            text("SELECT COUNT(*) FROM vehicle WHERE status='Healthy'")
        ).scalar()

        critical = conn.execute(
            text("SELECT COUNT(*) FROM vehicle WHERE status='Critical'")
        ).scalar()

        warning = conn.execute(
            text("SELECT COUNT(*) FROM vehicle WHERE status='Warning'")
        ).scalar()

    return {
        "healthy": healthy,
        "critical": critical,
        "warning": warning
    }

@app.get("/delete/{vehicle_id}")
def delete_vehicle(vehicle_id: int):

    with engine.connect() as conn:

        conn.execute(
            text("DELETE FROM vehicle WHERE id = :id"),
            {"id": vehicle_id}
        )

        conn.commit()

    return RedirectResponse(
    url="/dashboard",
    status_code=303
)

@app.get("/edit/{vehicle_id}", response_class=HTMLResponse)
def edit_vehicle(vehicle_id: int):

    with engine.connect() as conn:

        result = conn.execute(
            text("SELECT * FROM vehicle WHERE id = :id"),
            {"id": vehicle_id}
        )

        vehicle = result.fetchone()

    return f"""
    <html>
    <body>

        <form action="/update/{vehicle_id}" method="post">

            Vehicle ID:<br>
            <input type="text" name="vehicle_id_new" value="{vehicle[1]}"><br><br>

            Speed:<br>
            <input type="number" name="speed" value="{vehicle[2]}"><br><br>

            Engine Temperature:<br>
            <input type="number" name="engine_temp" value="{vehicle[3]}"><br><br>

            Fuel Level:<br>
            <input type="number" name="fuel_level" value="{vehicle[4]}"><br><br>

            Battery Voltage:<br>
            <input type="number" step="0.1" name="battery_voltage" value="{vehicle[5]}"><br><br>

            <button type="submit">
                Update Vehicle
            </button>

</form>

    </body>
    </html>
    """

@app.post("/update/{vehicle_id}")
def update_vehicle(
    vehicle_id: int,
    vehicle_id_new: str = Form(...),
    speed: int = Form(...),
    engine_temp: int = Form(...),
    fuel_level: int = Form(...),
    battery_voltage: float = Form(...)
):

    status = "Healthy"
   # dtc_code = ""
    #dtc_description = ""
    #created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


    if engine_temp > 100:
        status = "Critical"
        dtc_code = "P0118"
        dtc_description = "Engine Coolant Temperature High"


    elif fuel_level < 15:
        status = "Warning"
        dtc_code = "P0171"
        dtc_description = "Fuel System Too Lean"

    elif battery_voltage < 11:
        status = "Critical"
        dtc_code = "B1000"
        dtc_description = "Battery Voltage Low"

    with engine.connect() as conn:

        conn.execute(
            text("""
            UPDATE vehicle
            SET
                vehicle_id = :vehicle_id,
                speed = :speed,
                engine_temp = :engine_temp,
                fuel_level = :fuel_level,
                battery_voltage = :battery_voltage,
                status = :status,
                dtc_code = :dtc_code,
                dtc_description = :dtc_description
                WHERE id = :id
                 
            """),
            {
                "vehicle_id": vehicle_id_new,
                "speed": speed,
                "engine_temp": engine_temp,
                "fuel_level": fuel_level,
                "battery_voltage": battery_voltage,
                "status": status,
                "dtc_code": dtc_code,
                "dtc_description": dtc_description,
                "id": vehicle_id,
                
            }
        )

        conn.commit()

    return RedirectResponse(
        url="/dashboard",
        status_code=303
    )
@app.get("/simulate")
def simulate_vehicle():

    vehicle_id = f"TEST{random.randint(100,999)}"

    speed = random.randint(20,120)

    engine_temp = random.randint(60,130)

    fuel_level = random.randint(5,100)

    battery_voltage = round(
        random.uniform(9.5,13.5),
        1
    )

    status = "Healthy"

    dtc_code = ""

    dtc_description = ""

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


    if engine_temp > 100:

        status = "Critical"

        dtc_code = "P0118"

        dtc_description = "Engine Coolant Temperature High"

    elif fuel_level < 15:

        status = "Warning"

        dtc_code = "P0171"

        dtc_description = "Fuel System Too Lean"

    elif battery_voltage < 11:

        status = "Critical"

        dtc_code = "B1000"

        dtc_description = "Battery Voltage Low"

    with engine.connect() as conn:

        conn.execute(
            text("""
            INSERT INTO vehicle
            (
                vehicle_id,
                speed,
                engine_temp,
                fuel_level,
                battery_voltage,
                status,
                dtc_code,
                dtc_description,
                created_at
            )
            VALUES
            (
                :vehicle_id,
                :speed,
                :engine_temp,
                :fuel_level,
                :battery_voltage,
                :status,
                :dtc_code,
                :dtc_description,
                :created_at
            )
            """),
            {
                "vehicle_id": vehicle_id,
                "speed": speed,
                "engine_temp": engine_temp,
                "fuel_level": fuel_level,
                "battery_voltage": battery_voltage,
                "status": status,
                "dtc_code": dtc_code,
                "dtc_description": dtc_description,
                "created_at":created_at
            }
        )

        conn.commit()

    return RedirectResponse(
        url="/dashboard",
        status_code=303
    )
@app.get("/simulate-fleet")
def simulate_fleet(
    fleet_size: int = 10
):

    for i in range(fleet_size):

        vehicle_id = f"FLEET{random.randint(1000,9999)}"

        speed = random.randint(20,120)

        engine_temp = random.randint(60,130)

        fuel_level = random.randint(5,100)

        battery_voltage = round(
            random.uniform(9.5,13.5),
            1
        )

        status = "Healthy"

        dtc_code = ""

        dtc_description = ""

        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if engine_temp > 100:

            status = "Critical"

            dtc_code = "P0118"

            dtc_description = "Engine Coolant Temperature High"

        elif fuel_level < 15:

            status = "Warning"

            dtc_code = "P0171"

            dtc_description = "Fuel System Too Lean"

        elif battery_voltage < 11:

            status = "Critical"

            dtc_code = "B1000"

            dtc_description = "Battery Voltage Low"

        with engine.connect() as conn:

            conn.execute(
                text("""
                INSERT INTO vehicle
                (
                    vehicle_id,
                    speed,
                    engine_temp,
                    fuel_level,
                    battery_voltage,
                    status,
                    dtc_code,
                    dtc_description,
                    created_at
                )
                VALUES
                (
                    :vehicle_id,
                    :speed,
                    :engine_temp,
                    :fuel_level,
                    :battery_voltage,
                    :status,
                    :dtc_code,
                    :dtc_description,
                    :created_at
                )
                """),
                {
                    "vehicle_id": vehicle_id,
                    "speed": speed,
                    "engine_temp": engine_temp,
                    "fuel_level": fuel_level,
                    "battery_voltage": battery_voltage,
                    "status": status,
                    "dtc_code": dtc_code,
                    "dtc_description": dtc_description,
                    "created_at": created_at
                }
            )

            conn.commit()

    return RedirectResponse(
        url="/dashboard",
        status_code=303
    )