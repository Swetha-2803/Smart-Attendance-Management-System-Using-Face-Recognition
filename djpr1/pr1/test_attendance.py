<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Attendance Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        td, th { vertical-align: middle; text-align: center; }
        .small-img { width:60px; height:60px; object-fit:cover; border-radius:50%; }
    </style>
</head>
<body class="container mt-4">

<h2 class="text-center mb-4">📊 Student Attendance Dashboard</h2>

<!-- Filter Form -->
<form method="get" class="row g-3 mb-3">
    <div class="col-auto">
        <label for="start_date" class="form-label">Start Date</label>
        <input type="date" name="start_date" id="start_date" class="form-control" value="{{ request.GET.start_date|default:today }}">
    </div>
    <div class="col-auto">
        <label for="end_date" class="form-label">End Date</label>
        <input type="date" name="end_date" id="end_date" class="form-control" value="{{ request.GET.end_date|default:today }}">
    </div>
    <div class="col-auto align-self-end">
        <button type="submit" class="btn btn-primary">Filter</button>
        <a href="{% url 'attendance_dashboard' %}" class="btn btn-secondary">Reset</a>
    </div>
</form>

<!-- Period Stats Summary -->
<div class="row mb-3">
    {% for period, stats in period_stats.items %}
        <div class="col-md-3 mb-2">
            <div class="card">
                <div class="card-body">
                    <h6 class="card-title">{{ period|capfirst }}</h6>
                    <p class="mb-1">Present: <strong>{{ stats.present }}</strong></p>
                    <p class="mb-0">Absent: <strong>{{ stats.absent }}</strong></p>
                </div>
            </div>
        </div>
    {% endfor %}
</div>

<!-- Attendance Table -->
<table class="table table-bordered table-striped">
    <thead class="table-dark">
        <tr>
            <th>ID</th>
            <th>Student Name</th>
            <th>Roll No</th>
            <th>Image</th>
            <th>P1</th>
            <th>P2</th>
            <th>P3</th>
            <th>P4</th>
            <th>P5</th>
            <th>P6</th>
            <th>P7</th>
            <th>Date</th>
            <th>Time</th>
        </tr>
    </thead>
    <tbody>
        {% for record in records %}
        <tr>
            <td>{{ forloop.counter }}</td>
            <td>{{ record.student.student_name }}</td>
            <td>{{ record.student.student_rollno }}</td>
            <td>
                {% if record.student.student_image %}
                    <img src="{{ record.student.student_image.url }}" class="small-img">
                {% else %}
                    No Image
                {% endif %}
            </td>
            {% for period in "period1 period2 period3 period4 period5 period6 period7"|split:" " %}
                <td>
                    {% if record|attr:period == "Present" %}
                        <span class="badge bg-success">{{ record|attr:period }}</span>
                    {% else %}
                        <span class="badge bg-danger">{{ record|attr:period|default:"A" }}</span>
                    {% endif %}
                </td>
            {% endfor %}
            <td>{{ record.date }}</td>
            <td>{{ record.time }}</td>
        </tr>
        {% empty %}
        <tr>
            <td colspan="13" class="text-center">No Attendance Records Found</td>
        </tr>
        {% endfor %}
    </tbody>
</table>

</body>
</html>
