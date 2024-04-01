'''
 # @ Create Time: 2024-04-01 16:48:09.342644
'''

from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd

app = Dash(__name__, title="Non-thermal plasma decontamination efficacy")

server = app.server

# Load your dataset
file_path = 'https://raw.githubusercontent.com/gpampoukis/ntp_interactive_plot/583c584b00ce5d7ae4ba3bc89145cd9e12a9d5a7/my_dataframe.csv'
df = pd.read_csv(file_path)

# Extract unique values for matrix_category, genus, upper_electrode_shape (if available)
genus_values = df['genus'].unique() if 'genus' in df.columns else []
matrix_category_values = df['matrix_category'].unique() if 'matrix_category' in df.columns else []
upper_electrode_shape_values = df['upper_electrode_shape'].unique() if 'upper_electrode_shape' in df.columns else []

# Define the layout of the Dash application
app.layout = html.Div([
    # Title of the dashboard
    html.H4('Overview of the D-values obtained for DBD plotted against the dissipated power per plasma volume'),

    # Graph component to display the scatter plot
    dcc.Graph(id="scatter-plot"),

    # Slider for filtering by medium area_of_the_sample_cm2
    html.P("Filter by area_of_the_sample_cm2:"),
    dcc.RangeSlider(
        id='area_of_the_sample_cm2-range-slider', 
        min=df['area_of_the_sample_cm2'].min(), 
        max=df['area_of_the_sample_cm2'].max(), 
        value=[df['area_of_the_sample_cm2'].min(), df['area_of_the_sample_cm2'].max()]
    ),

    # Slider for filtering by food pH
    html.P("Filter by ph_before:"),
    dcc.RangeSlider(
        id='ph-range-slider', 
        min=df['ph_before'].min(), 
        max=df['ph_before'].max(), 
        value=[df['ph_before'].min(), df['ph_before'].max()]
    ),

    # Dropdown for selecting matrix_category values
    html.P("Select matrix_category:"),
    dcc.Dropdown(
        id='matrix_category-dropdown', 
        options=[{'label': i, 'value': i} for i in matrix_category_values], 
        value=matrix_category_values[0],
        multi=True
    ),

    # Dropdown for selecting upper_electrode_shape values
    html.P("Select upper_electrode_shape:"),
    dcc.Dropdown(
        id='upper_electrode_shape-dropdown', 
        options=[{'label': i, 'value': i} for i in upper_electrode_shape_values], 
        value=upper_electrode_shape_values[0],
        multi=True
    )
])


@app.callback(
    Output("scatter-plot", "figure"), 
    [Input("ph-range-slider", "value"), 
     Input("area_of_the_sample_cm2-range-slider", "value"),
     Input("matrix_category-dropdown", "value"),
     Input("upper_electrode_shape-dropdown", "value")]
)

def update_bar_chart(ph_before_range, area_of_the_sample_cm2_range, selected_matrix_categories, selected_upper_electrode_shapes):
   """
    Updates the scatter plot based on the selected filters.

    Parameters:
    - ph_before_range: A tuple representing the selected range of food pH values.
    - area_of_the_sample_cm2: A tuple representing the selected range of area_of_the_sample_cm2 values.
    - selected_matrix_categories: A list of selected matrix_category values to filter the dataset.
    - selected_upper_electrode_shapes: A list of selected upper_electrode_shape values to filter the dataset.
    
    Returns:
    - A plotly express figure object that represents the updated scatter plot.
    """ 
   
   mask = (
        df['ph_before'].between(*ph_before_range) &
        df['area_of_the_sample_cm2'].between(*area_of_the_sample_cm2_range) &
        df['matrix_category'].isin(selected_matrix_categories if isinstance(selected_matrix_categories, list) else [selected_matrix_categories]) &
        df['upper_electrode_shape'].isin(selected_upper_electrode_shapes if isinstance(selected_upper_electrode_shapes, list) else [selected_upper_electrode_shapes])
    )
   
   fig = px.scatter(
        df[mask], 
        x="dis_W_cm3_of_plasma_volume", 
        y="logd_log_min", 
        color="genus", 
        size='area_of_the_sample_cm2', 
        hover_data=['area_of_the_sample_cm2', 'ph_before', 'matrix_category', 'upper_electrode_shape'],
    )
   
   return fig

if __name__ == '__main__':
    app.run_server(debug=True)
