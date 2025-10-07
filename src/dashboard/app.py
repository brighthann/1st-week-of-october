# Streamlit dashboard for API monitoring
import streamlit as st
import requests
import pandas as pd
import time
import os
from datetime import datetime

from components.charts import (
    create_response_time_chart,
    create_uptime_chart,
    create_status_pie_chart,
)

# Page configuration
st.set_page_config(
    page_title="API Health Monitor", layout="wide", initial_sidebar_state="expanded"
)

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
REFRESH_INTERVAL = 30  # seconds

# Status color mapping
STATUS_COLORS = {
    "healthy": "#00ff00",  # Green
    "unhealthy": "#ff0000",  # Red
    "timeout": "#ffaa00",  # Orange
    "error": "#ff00ff",  # Purple
}

# Status indicator using colored circles
STATUS_INDICATORS = {
    "healthy": "#00ff00",  # Green
    "unhealthy": "#ff0000",  # Red
    "timeout": "#ffaa00",  # Orange
    "error": "#ff00ff",  # Purple
}

# Custom CSS
st.markdown(
    """
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .status-healthy {
        color: #00ff00;
        font-weight: bold;
    }
    .status-unhealthy {
        color: #ff0000;
        font-weight: bold;
    }
    .status-timeout {
        color: #ffaa00;
        font-weight: bold;
    }
    .status-error {
        color: #ff00ff;
        font-weight: bold;
    }
    .status-indicator {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 8px;
    }
</style>
""",
    unsafe_allow_html=True,
)


# Helper functions
@st.cache_data(ttl=30)
def fetch_api_data(endpoint: str):
    """Fetch data from API with caching."""
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API returned status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to connect to API: {e}")
        return None


def get_status_color(status: str) -> str:
    """Get color for status."""
    return STATUS_COLORS.get(status, "#808080")


def create_status_badge(status: str, name: str) -> str:
    """Create HTML status badge with colored indicator."""
    color = get_status_color(status)
    return f"""
    <div style="display: flex; align-items: center; margin-bottom: 10px;">
        <span class="status-indicator" style="background-color: {color};"></span>
        <span style="font-weight: bold;">{name}</span>
        <span style="margin-left: 10px; color: {color};">{status.upper()}</span>
    </div>
    """


def format_response_time(response_time: float) -> str:
    """Format response time with appropriate units."""
    if response_time is None:
        return "N/A"
    elif response_time < 1000:
        return f"{response_time:.0f}ms"
    else:
        return f"{response_time/1000:.2f}s"


# App title and description
st.title("API Health Monitor Dashboard")
st.markdown("Real-time monitoring of API endpoints")

# Sidebar
with st.sidebar:
    st.header("Controls")

    # Auto-refresh toggle
    auto_refresh = st.checkbox("Auto-refresh", value=True)
    refresh_interval = st.slider(
        "Refresh interval (seconds)", 10, 300, REFRESH_INTERVAL
    )

    # Manual refresh button
    if st.button("Refresh Now"):
        st.cache_data.clear()
        st.rerun()

    st.header("Quick Stats")

    # Fetch overall health
    health_data = fetch_api_data("/health/endpoints")
    if health_data:
        st.metric("Total Endpoints", health_data.get("total_endpoints", 0))
        st.metric("Healthy", health_data.get("healthy_endpoints", 0))
        st.metric("Unhealthy", health_data.get("unhealthy_endpoints", 0))

        overall_status = health_data.get("status", "unknown")
        status_color = get_status_color(
            "healthy" if overall_status == "healthy" else "unhealthy"
        )
        st.markdown(
            f'<p style="color: {status_color}; font-weight: bold; font-size: 1.2em;">'
            f"{overall_status.upper()}</p>",
            unsafe_allow_html=True,
        )

# Main content
if auto_refresh:
    # Auto-refresh placeholder
    placeholder = st.empty()

    # Auto-refresh loop
    while auto_refresh:
        with placeholder.container():
            # Fetch current status
            status_data = fetch_api_data("/api/status")

            if status_data:
                # Current status cards
                st.header("Current Status")

                # Create columns for status cards
                cols = st.columns(len(status_data))

                for i, endpoint in enumerate(status_data):
                    with cols[i]:
                        status = endpoint["status"]
                        response_time = format_response_time(
                            endpoint.get("response_time")
                        )
                        uptime = endpoint.get("uptime_percentage", 100)

                        # Status badge
                        st.markdown(
                            create_status_badge(status, endpoint["name"]),
                            unsafe_allow_html=True,
                        )

                        # Metrics
                        st.metric(
                            label="Response Time", value=response_time, delta=None
                        )
                        st.metric(label="Uptime", value=f"{uptime:.1f}%", delta=None)

                        # Additional details in expander
                        with st.expander("Details"):
                            st.write(f"**URL:** {endpoint['url']}")
                            st.write(
                                f"**Status Code:** "
                                f"{endpoint.get('status_code', 'N/A')}"
                            )
                            st.write(
                                f"**Last Check:** "
                                f"{endpoint.get('timestamp', 'N/A')}"
                            )
                            if endpoint.get("error"):
                                st.error(f"Error: {endpoint['error']}")
                            if endpoint.get("ssl_expires"):
                                st.write(
                                    f"**SSL Expires:** " f"{endpoint['ssl_expires']}"
                                )

                # Charts section
                st.header("Analytics")

                chart_col1, chart_col2 = st.columns(2)

                with chart_col1:
                    # Response time chart
                    st.plotly_chart(
                        create_response_time_chart(status_data),
                        use_container_width=True,
                    )

                with chart_col2:
                    # Uptime chart
                    st.plotly_chart(
                        create_uptime_chart(status_data), use_container_width=True
                    )

                # Status distribution
                st.plotly_chart(
                    create_status_pie_chart(status_data), use_container_width=True
                )

                # Recent alerts
                st.header("Recent Alerts")
                alerts_data = fetch_api_data("/api/alerts")

                if alerts_data and alerts_data.get("alerts"):
                    alerts_df = pd.DataFrame(alerts_data["alerts"])

                    # Alert color mapping
                    alert_colors = {
                        "downtime": "#ff0000",  # Red
                        "recovery": "#00ff00",  # Green
                        "slow_response": "#ffaa00",  # Orange
                        "ssl_expiry": "#ff00ff",  # Purple
                    }

                    # Display recent alerts
                    for _, alert in alerts_df.head(10).iterrows():
                        alert_type = alert.get("type", "unknown")
                        alert_endpoint = alert.get("endpoint", "unknown")
                        alert_time = alert.get("timestamp", "unknown")

                        color = alert_colors.get(alert_type, "#808080")

                        st.markdown(
                            f'<div style="padding: 10px; margin: 5px 0; '
                            f"border-left: 4px solid {color}; "
                            f'background-color: #f0f2f6;">'
                            f"<strong>{alert_endpoint}</strong> - "
                            f"{alert_type} at {alert_time}"
                            f"</div>",
                            unsafe_allow_html=True,
                        )
                else:
                    st.info("No recent alerts")

                # Performance metrics table
                st.header("Detailed Metrics")

                if status_data:
                    metrics_data = []
                    for endpoint in status_data:
                        metrics_data.append(
                            {
                                "Endpoint": endpoint["name"],
                                "Status": endpoint["status"],
                                "Response Time": format_response_time(
                                    endpoint.get("response_time")
                                ),
                                "Status Code": endpoint.get("status_code", "N/A"),
                                "Uptime %": f"{endpoint.get('uptime_percentage', 100):.2f}%",
                                "Last Check": endpoint.get("timestamp", "N/A"),
                            }
                        )

                    metrics_df = pd.DataFrame(metrics_data)

                    # Style the dataframe
                    def highlight_status(row):
                        color = get_status_color(row["Status"])
                        return [
                            f"background-color: {color}20" if col == "Status" else ""
                            for col in row.index
                        ]

                    styled_df = metrics_df.style.apply(highlight_status, axis=1)
                    st.dataframe(styled_df, use_container_width=True)

                # Last updated timestamp
                st.caption(
                    f"Last updated: " f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )

            else:
                st.error("Failed to fetch data from API")

        # Wait before next refresh
        time.sleep(refresh_interval)

else:
    # Static mode - no auto-refresh
    st.info("Auto-refresh is disabled. " "Use the refresh button to update data.")

    # Fetch and display current data
    status_data = fetch_api_data("/api/status")

    if status_data:
        # Display the same content as auto-refresh mode
        st.header("Current Status")

        cols = st.columns(len(status_data))

        for i, endpoint in enumerate(status_data):
            with cols[i]:
                status = endpoint["status"]
                response_time = format_response_time(endpoint.get("response_time"))
                uptime = endpoint.get("uptime_percentage", 100)

                # Status badge
                st.markdown(
                    create_status_badge(status, endpoint["name"]),
                    unsafe_allow_html=True,
                )

                # Metrics
                st.metric(label="Response Time", value=response_time)
                st.metric(label="Uptime", value=f"{uptime:.1f}%")
