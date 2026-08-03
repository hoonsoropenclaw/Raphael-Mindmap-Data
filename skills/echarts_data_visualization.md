# ECharts Data Visualization

## Overview
This micro-skill focuses on using the ECharts library to render various data visualizations, including tree diagrams, timelines, and other interactive chart types. It provides comprehensive guidance on setting up, configuring, and interacting with ECharts visualizations.

## Key Features
- **Tree Diagram Rendering**: Create hierarchical tree structures with interactive features such as mouse hover, click, and double-click events.
- **Timeline Visualization**: Display data over time with customizable time intervals and interactive controls.
- **Customization**: Highly configurable chart options to tailor the appearance and behavior of the visualizations.
- **Event Handling**: Implement event listeners for user interactions, such as clicks and hovers, to enhance interactivity.

## Implementation Steps

### 1. Setting Up the ECharts Instance
Initialize the ECharts instance by targeting a specific DOM element.

```javascript
const chart = echarts.init(document.getElementById('chart-container'));
```

### 2. Configuring Chart Options
Define the chart configuration using the `option` object. This includes setting up the chart type, data, layout, and styling.

#### Tree Diagram Configuration
```javascript
const treeOption = {
  tooltip: { 
    trigger: 'item', 
    triggerOn: 'mousemove' 
  },
  series: [{
    type: 'tree',
    data: [data], // Replace with your tree data
    top: '1%',
    left: '7%',
    bottom: '1%',
    right: '20%',
    symbolSize: 7,
    label: { 
      position: 'left', 
      verticalAlign: 'middle', 
      align: 'right' 
    },
    leaves: { 
      label: { 
        position: 'right', 
        align: 'left', 
        verticalAlign: 'middle' 
      } 
    },
    expandAndCollapse: true,
    animationDuration: 550,
    animationDurationUpdate: 750,
    initialTreeDepth: 2
  }]
};
```

#### Timeline Configuration
```javascript
const timelineOption = {
  tooltip: { 
    trigger: 'axis' 
  },
  xAxis: {
    type: 'time',
    data: timelineData // Replace with your timeline data
  },
  yAxis: {
    type: 'value'
  },
  series: [{
    type: 'line',
    data: timelineSeriesData // Replace with your timeline series data
  }]
};
```

### 3. Rendering the Chart
Set the configured options to the ECharts instance and render the chart.

```javascript
chart.setOption(treeOption); // or timelineOption
```

### 4. Handling User Interactions
Attach event listeners to handle user interactions such as clicks, hovers, and other custom events.

```javascript
chart.on('click', function (params) {
  // Handle click event
  console.log(params);
});

chart.on('mouseover', function (params) {
  // Handle mouseover event
  console.log(params);
});
```

## Common Issues and Troubleshooting

### Issue 1: Chart Not Rendering
- **Cause**: Incorrect DOM element ID, missing data, or ECharts not properly initialized.
- **Solution**: 
  - Verify that the DOM element ID matches the one used in `echarts.init()`.
  - Ensure that the data is correctly formatted and loaded.
  - Check for any JavaScript errors in the console that might prevent the chart from rendering.

### Issue 2: Interactive Events Not Triggering
- **Cause**: Event listeners not properly attached or other code interfering with event propagation.
- **Solution**: 
  - Confirm that event listeners are correctly bound to the chart instance.
  - Use browser developer tools to check if events are being triggered and not blocked by other scripts.

### Issue 3: Performance Problems with Large Datasets
- **Cause**: Rendering complex charts with extensive data can slow down the application.
- **Solution**: 
  - Optimize data by aggregating or simplifying the dataset.
  - Use ECharts' built-in performance optimization features, such as progressive rendering or data sampling.

## Best Practices

- **Data Validation**: Always validate and sanitize data before rendering to prevent errors and security issues.
- **Responsive Design**: Ensure that charts are responsive and adapt to different screen sizes by listening to window resize events and updating the chart size accordingly.
- **Accessibility**: Implement accessibility features such as keyboard navigation and ARIA labels to make visualizations usable for all users.

## Example: Combining Tree and Timeline
```javascript
const combinedOption = {
  tooltip: { 
    trigger: 'item', 
    triggerOn: 'mousemove' 
  },
  series: [{
    type: 'tree',
    data: [treeData],
    top: '1%',
    left: '7%',
    bottom: '1%',
    right: '20%',
    symbolSize: 7,
    label: { 
      position: 'left', 
      verticalAlign: 'middle', 
      align: 'right' 
    },
    leaves: { 
      label: { 
        position: 'right', 
        align: 'left', 
        verticalAlign: 'middle' 
      } 
    },
    expandAndCollapse: true,
    animationDuration: 550,
    animationDurationUpdate: 750,
    initialTreeDepth: 2
  },
  {
    type: 'line',
    data: timelineSeriesData,
    xAxisIndex: 1
  }]
};
```

By following this guide, you can effectively utilize ECharts to create dynamic and interactive data visualizations tailored to your application's needs.