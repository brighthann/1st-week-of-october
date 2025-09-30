#Dashboard chart components
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any

def create_response_time_chart(statuses: List[Dict[str, Any]]) -> go.Figure:
    """Create response time trend chart."""
    if not statuses:
        fig = go.Figure()
        fig.add_annotation(text="No data available", xref="paper", yref="paper", 
                          x=0.5, y=0.5, showarrow=False)
        return fig
    
    df = pd.DataFrame(statuses)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    fig = go.Figure()
    
    for endpoint in df['name'].unique():
        endpoint_data = df[df['name'] == endpoint]
        fig.add_trace(go.Scatter(
            x=endpoint_data['timestamp'],
            y=endpoint_data['response_time'],
            mode='lines+markers',
            name=endpoint,
            line=dict(width=2),
            marker=dict(size=6)
        ))
    
    fig.update_layout(
        title="Response Time Trends",
        xaxis_title="Time",
        yaxis_title="Response Time (ms)",
        hovermode='x unified',
        template="plotly_white"
    )
    
    return fig

def create_uptime_chart(statuses: List[Dict[str, Any]]) -> go.Figure:
    """Create uptime percentage chart."""
    if not statuses:
        return go.Figure()
    
    df = pd.DataFrame(statuses)
    
    fig = go.Figure(data=[
        go.Bar(
            x=df['name'],
            y=df['uptime_percentage'],
            text=[f"{up:.1f}%" for up in df['uptime_percentage']],
            textposition='auto',
            marker_color=['#00ff00' if up >= 99 else '#ffaa00' if up >= 95 else '#ff0000' 
                         for up in df['uptime_percentage']]
        )
    ])
    
    fig.update_layout(
        title="Uptime Percentage (24h)",
        xaxis_title="Endpoint",
        yaxis_title="Uptime %",
        yaxis=dict(range=[0, 100]),
        template="plotly_white"
    )
    
    return fig

def create_status_pie_chart(statuses: List[Dict[str, Any]]) -> go.Figure:
    """Create status distribution pie chart."""
    if not statuses:
        return go.Figure()
    
    df = pd.DataFrame(statuses)
    status_counts = df['status'].value_counts()
    
    colors = {
        'healthy': '#00ff00',
        'unhealthy': '#ff0000',
        'timeout': '#ffaa00',
        'error': '#ff00ff'
    }
    
    fig = go.Figure(data=[go.Pie(
        labels=status_counts.index,
        values=status_counts.values,
        marker_colors=[colors.get(status, '#cccccc') for status in status_counts.index]
    )])
    
    fig.update_layout(
        title="Current Status Distribution",
        template="plotly_white"
    )
    
    return fig