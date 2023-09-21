import React from "react";
import PropTypes from "prop-types";
import { TrendLine, FibonacciRetracement, DrawingObjectSelector, InteractiveYCoordinate } from "react-stockcharts/lib/interactive";
import { scaleTime } from "d3-scale";
import { format } from "d3-format";
import { timeFormat } from "d3-time-format";
import shortid from "shortid";
import {Modal,Button,FormGroup,ControlLabel,FormControl,} from "react-bootstrap";
import { ChartCanvas, Chart } from "react-stockcharts";
import {BarSeries,AreaSeries,CandlestickSeries,RSISeries,BollingerSeries,LineSeries,MACDSeries,} from "react-stockcharts/lib/series";
import { XAxis, YAxis } from "react-stockcharts/lib/axes";
import { CrossHairCursor,EdgeIndicator,CurrentCoordinate,MouseCoordinateX,  MouseCoordinateY,} from "react-stockcharts/lib/coordinates";
import { discontinuousTimeScaleProvider } from "react-stockcharts/lib/scale";
import {OHLCTooltip,MovingAverageTooltip, BollingerBandTooltip,RSITooltip,SingleValueTooltip,MACDTooltip,HoverTooltip} from "react-stockcharts/lib/tooltip";
import { ema, macd, rsi, sma, atr, bollingerBand } from "react-stockcharts/lib/indicator";
import { fitWidth } from "react-stockcharts/lib/helper";
import { getMorePropsForChart } from "react-stockcharts/lib/interactive/utils";
import { head, last, toObject } from "react-stockcharts/lib/utils";
import {saveInteractiveNodes,getInteractiveNodes,} from "./interactiveutils";

function tooltipContent(ys) {
	return ({ currentItem, xAccessor }) => {
		return {
			x: dateFormat(xAccessor(currentItem)),
			y: [
				{
					label: "open",
					value: currentItem.open && numberFormat(currentItem.open)
				},
				{
					label: "high",
					value: currentItem.high && numberFormat(currentItem.high)
				},
				{
					label: "low",
					value: currentItem.low && numberFormat(currentItem.low)
				},
				{
					label: "close",
					value: currentItem.close && numberFormat(currentItem.close)
				}
			]
				.concat(
					ys.map(each => ({
						label: each.label,
						value: each.value(currentItem),
						stroke: each.stroke
					}))
				)
				.filter(line => line.value)
		};
	};
}

    function round(number, precision = 0) {
        const d = Math.pow(10, precision);
        return Math.round(number * d) / d;
    }

    class Dialog extends React.Component {
        constructor(props) { super(props);
            //this.state = { alert: props.alert || {}, }; // Adicione um valor padrão aqui
            this.state = {alert: props.alert || {yValue: 0},};
            //this.state = {alert: props.alert,};
            this.handleChange = this.handleChange.bind(this);
            this.handleSave = this.handleSave.bind(this); }
        componentWillReceiveProps(nextProps) {this.setState({ alert: nextProps.alert || {yValue: 0},});}
        handleChange(e) { const { alert } = this.state; this.setState({ alert: { ...alert, yValue: Number(e.target.value),} });}
        handleSave() { this.props.onSave(this.state.alert, this.props.chartId); }

        render() {
            const { showModal, onClose, onDeleteAlert,} = this.props;
            const { alert } = this.state;

            if (!showModal) return null;
            return (
                <Modal show={showModal} onHide={onClose} >
                    <Modal.Header closeButton>
                        <Modal.Title>Edit Alert</Modal.Title>
                    </Modal.Header>

                    <Modal.Body>
                        <form>
                            <FormGroup controlId="text">
                                <ControlLabel>Alert when crossing</ControlLabel>
                                <FormControl type="number" value={alert.yValue} onChange={this.handleChange} />
                            </FormGroup>
                        </form>
                    </Modal.Body>

                    <Modal.Footer>
                        <Button bsStyle="danger" onClick={onDeleteAlert}>Delete Alert</Button>
                        <Button bsStyle="primary" onClick={this.handleSave}>Save</Button>
                    </Modal.Footer>
                </Modal>
            );
        }
    }

    const dateFormat = timeFormat("%Y-%m-%d");
    const numberFormat = format(".2f");
    const keyValues = ["high", "low"];

    const macdAppearance = {
        stroke: {
            macd: "#FF0000",
            signal: "#00F300",
        },
        fill: {
            divergence: "#4682B4"
        },
    };

    const alert = InteractiveYCoordinate.defaultProps.defaultPriceCoordinate;
    const sell = {
        ...InteractiveYCoordinate.defaultProps.defaultPriceCoordinate,
        stroke: "#E3342F",
        textFill: "#E3342F",
        text: "Sell 320",
        edge: {
            ...InteractiveYCoordinate.defaultProps.defaultPriceCoordinate.edge,
            stroke: "#E3342F"
        }
    };
    const buy = {
        ...InteractiveYCoordinate.defaultProps.defaultPriceCoordinate,
        stroke: "#1F9D55",
        textFill: "#1F9D55",
        text: "Buy 120",
        edge: {
            ...InteractiveYCoordinate.defaultProps.defaultPriceCoordinate.edge,
            stroke: "#1F9D55"
        }
    };

    const bbStroke = {
        top: "#f64B00",
        middle: "#000000",
        bottom: "#f64B00",
    };

    const bbFill = "#4682B4";



class CandleStickChartWithFibonacciInteractiveIndicator extends React.Component {

    //FIBONACCI
    removeRandomValues(data) {
		return data.map(item => {
			const newItem = { ...item };
			const numberOfDeletion =
				Math.floor(Math.random() * keyValues.length) + 1;
			for (let i = 0; i < numberOfDeletion; i += 1) {
				const randomKey =
					keyValues[Math.floor(Math.random() * keyValues.length)];
				newItem[randomKey] = undefined;
			}
			return newItem;
		});
	}

    //ALERTA e //FIBONACCI

    constructor(props) {
		super(props);
		this.onKeyPress = this.onKeyPress.bind(this);
		this.onDragComplete = this.onDragComplete.bind(this);
		this.onDelete = this.onDelete.bind(this);
		this.handleChoosePosition = this.handleChoosePosition.bind(this);
		this.saveInteractiveNodes = saveInteractiveNodes.bind(this);
		this.getInteractiveNodes = getInteractiveNodes.bind(this);
		this.handleSelectionAlert = this.handleSelectionAlert.bind(this);
        this.handleSelectionFib = this.handleSelectionFib.bind(this);
		this.saveCanvasNode = this.saveCanvasNode.bind(this);
		this.handleDialogClose = this.handleDialogClose.bind(this);
		this.handleChangeAlert = this.handleChangeAlert.bind(this);
		this.handleDeleteAlert = this.handleDeleteAlert.bind(this);
		this.handleDoubleClickAlert = this.handleDoubleClickAlert.bind(this);
        this.onFibComplete1 = this.onFibComplete1.bind(this);
        this.onFibComplete3 = this.onFibComplete3.bind(this);
        this.onDrawCompleteChart1 = this.onDrawCompleteChart1.bind(this);
		this.onDrawCompleteChart3 = this.onDrawCompleteChart3.bind(this);
		this.handleSelection = this.handleSelection.bind(this);


		this.state = {
		    enableTrendLine: false,
		    trends_1: [],
			trends_3: [],
		    enableFib: false,
            retracements_1: [],
            retracements_3: [],
			enableInteractiveObject: false,
			yCoordinateList_1: [],
			yCoordinateList_3: [],
			showModal: false,
			alertToEdit: {},
			selectedElement: null
		};
	}


//Trendline
	saveCanvasNode(node) {
		this.canvasNode = node;
	}

	componentDidMount() {
		document.addEventListener("keyup", this.onKeyPress);
	}

	componentWillUnmount() {
		document.removeEventListener("keyup", this.onKeyPress);
	}

	handleSelection(interactives) {
	    console.log("handleSelection(TrendLine) chamado");
		const state = toObject(interactives, each => {
			return [
				`trends_${each.chartId}`,
				each.objects,
			];
		});
		this.setState(state);
	}

    onDrawCompleteChart1(trends_1) {
      console.log(trends_1);
      const newTrends = trends_1.map(trend => ({ ...trend, selected: false }));
      this.setState({
        enableTrendLine: false,
        trends_1: newTrends,
        selectedElement: trends_1[trends_1.length - 1], // o último elemento desenhado
      });
    }

    // Esta é a nova função
      selectTrendLine = (index) => {
        const newTrends = this.state.trends_1.map((trend, i) => {
          if (i === index) {
            return { ...trend, selected: true };
          }
          return trend;
        });
        this.setState({ trends_1: newTrends });
      }

	onDrawCompleteChart3(trends_3) {
		// this gets called on
		// 1. draw complete of trendline
		// 2. drag complete of trendline
		console.log(trends_3);
		this.setState({
			enableTrendLine: false,
			trends_3
		});
	}

//FIBONACCI
	saveCanvasNode(node) {
		this.canvasNode = node;
	}
	componentDidMount() {
		document.addEventListener("keyup", this.onKeyPress);
	}
	componentWillUnmount() {
		document.removeEventListener("keyup", this.onKeyPress);
	}

    handleSelectionFib(interactives) {
        console.log("handleSelectionFib chamado");
		const state = toObject(interactives, each => {
			return [
				`retracements_${each.chartId}`,
				each.objects,
			];
		});
		this.setState(state);
	}

     onFibComplete1(retracements_1) {
        this.setState({
            retracements_1,
            enableFib: false,
            //selectedFib: null  // Adicione esta linha
        });
    }

    onFibComplete3(retracements_3) {
        this.setState({
            retracements_3,
            enableFib: false,
            //selectedFib: null  // Adicione esta linha
        });
    }

//Alerta

	saveCanvasNode(node) {
		this.canvasNode = node;
	}

	handleSelectionAlert(interactives, moreProps, e) {
	    console.log("handleSelectionAlert chamado");
		if (this.state.enableInteractiveObject) {
			const independentCharts = moreProps.currentCharts.filter(d => d !== 2);
			if (independentCharts.length > 0) {
				const first = head(independentCharts);

				const morePropsForChart = getMorePropsForChart(moreProps, first);
				const {
					mouseXY: [, mouseY],
					chartConfig: { yScale },
				} = morePropsForChart;

				const yValue = round(yScale.invert(mouseY), 2);
				const newAlert = {
					...InteractiveYCoordinate.defaultProps.defaultPriceCoordinate,
					yValue,
					id: shortid.generate()
				};
				this.handleChoosePosition(newAlert, morePropsForChart, e);
			}
		} else {
			const state = toObject(interactives, each => {
				return [
					`yCoordinateList_${each.chartId}`,
					each.objects,
				];
			});
			this.setState(state);
		}


	}


	handleChoosePosition(alert, moreProps, e) {
        if (e) {
            e.stopPropagation();
        }
		const { id: chartId } = moreProps.chartConfig;
		this.setState({
			[`yCoordinateList_${chartId}`]: [
				...this.state[`yCoordinateList_${chartId}`],
				alert
			],
			enableInteractiveObject: false,
		});
	}

	handleDoubleClickAlert(item) {
		this.setState({
			showModal: true,
			alertToEdit: {
				alert: item.object,
				chartId: item.chartId,
			},
		});
	}

	handleChangeAlert(alert, chartId) {
		const yCoordinateList = this.state[`yCoordinateList_${chartId}`];
		const newAlertList = yCoordinateList.map(d => {
			return d.id === alert.id ? alert : d;
		});

		this.setState({
			[`yCoordinateList_${chartId}`]: newAlertList,
			showModal: false,
			enableInteractiveObject: false,
		});
	}

	handleDeleteAlert() {
		const { alertToEdit } = this.state;
		const key = `yCoordinateList_${alertToEdit.chartId}`;
		const yCoordinateList = this.state[key].filter(d => {
			return d.id !== alertToEdit.alert.id;
		});
		this.setState({
			showModal: false,
			alertToEdit: {},
			[key]: yCoordinateList
		});
	}

	handleDialogClose() {
		// cancel alert edit
		this.setState(state => {
			const { originalAlertList, alertToEdit } = state;
			const key = `yCoordinateList_${alertToEdit.chartId}`;
			const list = originalAlertList || state[key];

			return {
				showModal: false,
				[key]: list,
			};
		});
	}

	componentDidMount() {
		document.addEventListener("keyup", this.onKeyPress);
	}

	componentWillUnmount() {
		document.removeEventListener("keyup", this.onKeyPress);
	}

	onDelete(yCoordinate, moreProps) {
		this.setState(state => {
			const chartId = moreProps.chartConfig.id;
			const key = `yCoordinateList_${chartId}`;

			const list = state[key];
			return {
				[key]: list.filter(d => d.id !== yCoordinate.id)
			};
		});
	}

	onDragComplete(yCoordinateList, moreProps, draggedAlert) {
		// this gets called on drag complete of drawing object
		const { id: chartId } = moreProps.chartConfig;

		const key = `yCoordinateList_${chartId}`;
		const alertDragged = draggedAlert != null;

		this.setState({
			enableInteractiveObject: false,
			[key]: yCoordinateList,
			showModal: alertDragged,
			alertToEdit: {
				alert: draggedAlert,
				chartId,
			},
			originalAlertList: this.state[key],
		});
	}


    //ALERTA E //FIBONACCI
	onKeyPress(e) {
	 console.log("Key pressed:", e.which);  // Adicione esta linha
        const keyCode = e.which;
        switch (keyCode) {
            case 46: { // DEL
                // Para ALERTA
                this.setState({
                    yCoordinateList_1: this.state.yCoordinateList_1.filter(d => !d.selected),
                    yCoordinateList_3: this.state.yCoordinateList_3.filter(d => !d.selected)
                });

                // Para FIBONACCI
                const retracements_1 = this.state.retracements_1.filter(each => !each.selected);
                const retracements_3 = this.state.retracements_3.filter(each => !each.selected);
                this.canvasNode.cancelDrag();
                this.setState({
                    retracements_1,
                    retracements_3,
                });

                // Para Trendline
                const trends_1 = this.state.trends_1
                    .filter(each => !each.selected);
                const trends_3 = this.state.trends_3
                    .filter(each => !each.selected);

                this.setState({
                    trends_1,
                    trends_3,
                });

                break;
            }
            case 27: { // ESC
                // Para ALERTA
                this.canvasNode.cancelDrag();
                if (this.node) {
                    this.node.terminate();
                }
				this.setState({
					enableInteractiveObject: false
				});

                // Para FIBONACCI
                this.canvasNode.cancelDrag();
                if (this.node_1) {
                    this.node_1.terminate();
                }
                if (this.node_3) {
                    this.node_3.terminate();
                }

                this.setState({
                    enableFib: false
                });

                // Para Trendline
                this.canvasNode.cancelDrag();
                if (this.node_1) {
                    this.node_1.terminate();
                }
                if (this.node_3) {
                    this.node_3.terminate();
                }
                this.setState({
                    enableTrendLine: false
                });
                break;
            }

            case 68:   // D - Draw trendline
                case 69: { // E - Enable trendline
                this.setState({
                    enableTrendLine: true
                });
                break;
		}
        }

    }

    render() {

        const ema20 = ema()
			.options({
				windowSize: 20, // optional will default to 10
				sourcePath: "close", // optional will default to close as the source
			})
			.skipUndefined(true) // defaults to true
			.merge((d, c) => {d.ema20 = c;}) // Required, if not provided, log a error
			.accessor(d => d.ema20) // Required, if not provided, log an error during calculation
			.stroke("blue"); // Optional

        const ema26 = ema()
            .id(0)
            .options({ windowSize: 26 })
            .merge((d, c) => { d.ema26 = c; })
            .accessor(d => d.ema26);

        const ema12 = ema()
            .id(1)
            .options({ windowSize: 12 })
            .merge((d, c) => {d.ema12 = c;})
            .accessor(d => d.ema12);

        const sma20 = sma()
			.options({ windowSize: 20 })
			.merge((d, c) => {d.sma20 = c;})
			.accessor(d => d.sma20);

        const bb = bollingerBand()
			.merge((d, c) => {d.bb = c;})
			.accessor(d => d.bb);

        const macdCalculator = macd()
            .options({
                fast: 12,
                slow: 26,
                signal: 9,
            })
            .merge((d, c) => {d.macd = c;})
            .accessor(d => d.macd);

        const smaVolume50 = sma()
            .id(3)
            .options({
                windowSize: 50,
                sourcePath: "volume",
            })
            .merge((d, c) => {d.smaVolume50 = c;})
            .accessor(d => d.smaVolume50);


        const rsiCalculator = rsi()
        .options({ windowSize: 14 })
        .merge((d, c) => {d.rsi = c;})
        .accessor(d => d.rsi);

        const atr14 = atr()
        .options({ windowSize: 14 })
        .merge((d, c) => {d.atr14 = c;})
        .accessor(d => d.atr14);

        const { type, data: initialData, width, ratio } = this.props;
        const { showModal, alertToEdit } = this.state;
        //const calculatedData = macdCalculator(smaVolume50(ema12(ema26(initialData))));
        const calculatedData = sma20(bb(macdCalculator(ema26(ema12(smaVolume50(rsiCalculator(atr14(initialData))))))));
        const xScaleProvider = discontinuousTimeScaleProvider.inputDateAccessor(d => d.date);

        const { data, xScale, xAccessor, displayXAccessor } = xScaleProvider(initialData);
        //const {data,xScale,xAccessor,displayXAccessor,} = xScaleProvider(calculatedData);
        const start = xAccessor(last(data));
        const end = xAccessor(data[Math.max(0, data.length - 150)]);
        const xExtents = [start, end];


        const { gridProps } = this.props;
        const margin = { left: 70, right: 70, top: 20, bottom: 30 };
        //const height = 600;
        //const gridHeight = height - margin.top - margin.bottom;
        const gridWidth = width - margin.left - margin.right;
        const showGrid = true;
        const yGrid = showGrid ? { innerTickSize: -1 * gridWidth, tickStrokeDasharray: 'Solid', tickStrokeOpacity: 0.2, tickStrokeWidth: 1 } : {};
        const xGrid = showGrid ? { innerTickSize: -1 * gridWidth, tickStrokeDasharray: 'Solid', tickStrokeOpacity: 0.2, tickStrokeWidth: 1 } : {};




        return (
        <div className="dark">

            <button onClick={() => this.setState({ enableFib: true, enableInteractiveObject: false })}>
                Ativar Fibonacci
            </button>
            <button onClick={() => this.setState({ enableFib: false, enableInteractiveObject: true })}>
                Ativar Alerta
            </button>

                    <button onClick={() => this.selectTrendLine(0)}>Selecionar primeira linha de tendência</button>


          <ChartCanvas ref={this.saveCanvasNode}
            //style={{ zIndex: 2 }}
            height={750}
            ratio={ratio}
            width={width}
            margin={{ left: 70, right: 70, top: 20, bottom: 30 }}
            type={type}
            seriesName="MSFT"
            data={data}
            //xScale={scaleTime()} // Usando escala de tempo
            xScale={xScale}
            xAccessor={xAccessor}
            displayXAccessor={displayXAccessor}
            xExtents={xExtents}
          >

            <Chart id={1} height={450}
              yExtents={[d => [d.high, d.low], sma20.accessor(), ema20.accessor(), ema26.accessor(), ema12.accessor(), bb.accessor()]}
              //yExtents={[d => [d.high, d.low]]}
              padding={{ top: 10, bottom: 20 }}
              onContextMenu={(...rest) => { console.log("chart - context menu", rest); }}
            >

                <HoverTooltip
                    yAccessor={ema26.accessor()}
                    tooltipContent={tooltipContent([
                        {
                            label: `${ema12.type()}(${ema12.options()
                                .windowSize})`,
                            value: d => numberFormat(ema12.accessor()(d)),
                            stroke: ema12.stroke()
                        },
                        {
                            label: `${ema26.type()}(${ema26.options()
                                .windowSize})`,
                            value: d => numberFormat(ema26.accessor()(d)),
                            stroke: ema26.stroke()
                        }
                    ])}
                    fontSize={15}
                        bgOpacity={0} // torna o tooltip transparente
                        origin={() => [600, -20]} // Renderiza o tooltip no canto superior esquerdo

                />

              <XAxis
                //axisAt="bottom" orient="bottom" {...gridProps} {...xGrid} tickStroke="#FFFFFF" stroke="#FFFFFF"/>
                axisAt="bottom" orient="bottom" showTicks={false} outerTickSize={0} />
              <YAxis
                axisAt="right"
                orient="right"
                ticks={5}
                {...gridProps}
                {...yGrid}
                tickStroke="#FFFFFF"
                stroke="#FFFFFF"
                    onDoubleClick={(...rest) => { console.log("yAxis - double click", rest); }}
					onContextMenu={(...rest) => { console.log("yAxis - context menu", rest); }}

              />
              <MouseCoordinateX
                rectWidth={60}
                at="bottom"
                orient="bottom"
                displayFormat={timeFormat("%H:%M:%S")}
                fill="#3f48cc"
              />
              <MouseCoordinateY
                at="right"
                orient="right"
                displayFormat={format(".2f")}
                fill="#3f48cc"
              />
              <CandlestickSeries
                fill={d => d.close > d.open ? "green" : "#FF0000"}
                stroke={d => d.close > d.open ? "#6BA583" : "#ff3000"}
                wickStroke={d => d.close > d.open ? "#6BA583" : "#FF0000"}
              />

               <BollingerSeries yAccessor={d => d.bb}
                   stroke={bbStroke}
                   fill={bbFill} />

              <LineSeries yAccessor={ema26.accessor()} stroke={ema26.stroke()}/>
              <LineSeries yAccessor={ema12.accessor()} stroke={ema12.stroke()}/>
              <LineSeries yAccessor={sma20.accessor()} stroke={sma20.stroke()}/>
              <CurrentCoordinate yAccessor={sma20.accessor()} fill={sma20.stroke()} />
              <CurrentCoordinate yAccessor={ema26.accessor()} fill={ema26.stroke()} />
              <CurrentCoordinate yAccessor={ema12.accessor()} fill={ema12.stroke()} />

              <EdgeIndicator itemType="last" orient="right" edgeAt="right"
              yAccessor={d => d.close}
              fill={d => d.close > d.open ? "#6BA583" : "#FF0000"}
            />


              <OHLCTooltip
                origin={[-40, 0]}
                xDisplayFormat={timeFormat("%Y-%m-%d %H:%M:%S")}
                labelFill="#FFFFFF"
                textFill="#FFFFFF"
                ohlcFormat={format(".2f")}
                volumeFormat={format(".4s")}
              />

                <MovingAverageTooltip
                    onClick={e => console.log(e)}
                    origin={[-38, 15]}
                    options={[
                        {
                            yAccessor: ema26.accessor(),
                            type: ema26.type(),
                            stroke: ema26.stroke(),
                            windowSize: ema26.options().windowSize,
                        },
                        {
                            yAccessor: ema12.accessor(),
                            type: ema12.type(),
                            stroke: ema12.stroke(),
                            windowSize: ema12.options().windowSize,
                        },

                        {
                            yAccessor: sma20.accessor(),
                            type: sma20.type(),
                            stroke: sma20.stroke(),
                            windowSize: sma20.options().windowSize,
                        },

                    ]}
                />

                <BollingerBandTooltip
                    origin={[-38, 60]}
                    yAccessor={d => d.bb}
                    options={bb.options()} />


                <TrendLine
                    ref={this.saveInteractiveNodes("Trendline", 1)}
                    enabled={this.state.enableTrendLine}
                    type="LINE"
                    snap={false}

                    snapTo={d => [d.high, d.low]}
                    onStart={() => console.log("START")}
                    onComplete={this.onDrawCompleteChart1}
                    trends={this.state.trends_1}
                    appearance={{
                        stroke: "#ffca18",
                        strokeOpacity: 1,
                        strokeWidth: 1,
                        strokeDasharray: "Solid",
                        edgeStrokeWidth: 1,
                        edgeFill: "#FFFFFF",
                        edgeStroke: "#ffca18",
                        r: 6,
                    }}
                />


                <FibonacciRetracement
                    ref={this.saveInteractiveNodes("FibonacciRetracement", 1)}
                    enabled={this.state.enableFib}
                    type="BOUND"
                    retracements={this.state.retracements_1}
                    onComplete={this.onFibComplete1}
                    appearance={{
                        stroke: "#0024f3",
                        strokeWidth: 1,
                        strokeOpacity: 1,
                        fontFamily: "Helvetica Neue, Helvetica, Arial, sans-serif",
                        fontSize: 11,
                        fontFill: "#ffffff",
                        edgeStroke: "#0024f3",
                        edgeFill: "#FFFFFF",
                        nsEdgeFill: "#000000",
                        edgeStrokeWidth: 1,
                        r: 3,
                    }}
                />


                <InteractiveYCoordinate
                    ref={this.saveInteractiveNodes("InteractiveYCoordinate", 1)}
                    enabled={this.state.enableInteractiveObject}
                    onDragComplete={this.onDragComplete}
                    onDelete={this.onDelete}
                    yCoordinateList={this.state.yCoordinateList_1}
                />



            </Chart>

            <Chart id={2} height={100}
                yExtents={macdCalculator.accessor()}
                origin={(w, h) => [0, h - 150]} padding={{ top: 5, bottom: 5 }}
            >
                <XAxis axisAt="bottom" orient="bottom"/>
                <YAxis axisAt="right" orient="right" ticks={2} />
                <MouseCoordinateX
                    at="bottom"
                    orient="bottom"
                    displayFormat={timeFormat("%Y-%m-%d")} />
                <MouseCoordinateY
                    at="right"
                    orient="right"
                    displayFormat={format(".2f")} />

                <MACDSeries yAccessor={d => d.macd}
                    {...macdAppearance} />

                <MACDTooltip
                    origin={[-38, 10]}
                    yAccessor={d => d.macd}
                    options={macdCalculator.options()}
                    appearance={macdAppearance}
                />


            </Chart>
            <Chart id={3}
					yExtents={[0, 100]}
					height={100} origin={(w, h) => [0, h - 250]}
				>
					<XAxis axisAt="bottom" orient="bottom" showTicks={false} outerTickSize={0} />
					<YAxis axisAt="right"
						orient="right"
						tickValues={[30, 50, 70]}/>
					<MouseCoordinateY
						at="right"
						orient="right"
						displayFormat={format(".2f")} />

					<RSISeries yAccessor={d => d.rsi} />

					<RSITooltip origin={[-38, 15]}
						yAccessor={d => d.rsi}
						options={rsiCalculator.options()} />
			</Chart>


            <CrossHairCursor />

             <DrawingObjectSelector
                enabled={!this.state.enableTrendLine && !this.state.enableFib}
                getInteractiveNodes={this.getInteractiveNodes}
                drawingObjectMap={{
                    Trendline: "trends",
                    FibonacciRetracement: "retracements",
                    InteractiveYCoordinate: "yCoordinateList"

                }}
                onSelect={
                    this.state.enableTrendLine
                    ? this.handleSelection
                    : this.state.enableFib
                    ? this.handleSelectionFib
                    : this.handleSelectionAlert
                }
                onDoubleClick={this.handleDoubleClickAlert}
            />

          </ChartCanvas>

          <Dialog
            showModal={showModal}
            alert={alertToEdit.alert}
            chartId={alertToEdit.chartId}
            onClose={this.handleDialogClose}
            onSave={this.handleChangeAlert}
            onDeleteAlert={this.handleDeleteAlert}
          />

          </div>
        );
    }
}

CandleStickChartWithFibonacciInteractiveIndicator.propTypes = {
  data: PropTypes.array.isRequired,
  width: PropTypes.number.isRequired,
  ratio: PropTypes.number.isRequired,
  type: PropTypes.oneOf(["svg", "hybrid"]).isRequired,
};

CandleStickChartWithFibonacciInteractiveIndicator.defaultProps = {
  type: "svg",
};

CandleStickChartWithFibonacciInteractiveIndicator = fitWidth(CandleStickChartWithFibonacciInteractiveIndicator);

export default CandleStickChartWithFibonacciInteractiveIndicator;
