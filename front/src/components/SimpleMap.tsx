import React, {Component, useState} from 'react';
import GoogleMapReact from 'google-map-react';
import {ExclamationCircleOutlined} from "@ant-design/icons";

type MarkerProps = {
    children?: React.ReactNode,
    lat: number
    lng: number
    text: string
    courier?: number
    deliveryNumber?: number,
    startingPoint?: boolean
    droppedNode?: boolean
}

//.cluster-marker {
//   color: #fff;
//   background: #1978c8;
//   border-radius: 50%;
//   padding: 10px;
//   display: flex;
//   justify-content: center;
//   align-items: center;
// }
//
// .crime-marker {
//   background: none;
//   border: none;
// }
//
// .crime-marker img {
//   width: 25px;
// }

const colors = [
    "#900020",
    "#013A20",
    "#000000",
    "#ECF87F",
    "#FFAEBC",
    "#CDD193",
    "#67595E",
]

const Marker: React.FC<MarkerProps> = ({
   children,
   text,
   deliveryNumber ,
   courier,
   startingPoint,
   droppedNode
}) => (
    <>
        {droppedNode ?
            <ExclamationCircleOutlined size={20} style={{width: "20px", height: "20px"}}/> :
            <div
                className="cluster-marker"
                style={{
                    width: "20px",
                    height: "20px",
                    color: "#fff",
                    background: startingPoint ? "#FAD02C" : courier ? colors[courier] : "#900020",
                    borderRadius: "50%",
                    padding: "10px",
                    display: "flex",
                    justifyContent: "center",
                    alignItems: "center"
                }}
            >
                {deliveryNumber}
            </div>
        }
    </>
);
type PointType = {
  lat: number,
  lng: number
}

type Response = {
    routes: PointType[][],
    dropped_nodes: PointType[][]
}

type Props = {
    points: PointType[],
    addPoint: (points: PointType[]) => void,
    result: Response,
    showResult: boolean
}

export const SimpleMap: React.FC<Props> = ({
   points,
   addPoint,
   result,
   showResult
}) => {

    const center = {
      lat: 50.45466,
      lng: 30.5238
    }

    const addMapPoint = (event: PointType) => {
      addPoint(points.concat([{lat: event.lat, lng: event.lng}]))
    }
    return (
      // Important! Always set the container height explicitly
      <div style={{ height: '100vh', width: '60%', float: "right" }}>
        <GoogleMapReact
          bootstrapURLKeys={{ key: "AIzaSyCWYtTeal3a9ttpSA8HYHmgJ21k4gnVMOA" }}
          defaultCenter={center}
          defaultZoom={11}
          onClick={addMapPoint}
        >
            {console.log(result, 'result')}
            {  // {'routes': [{'lat': [50.4486941427873, 30.52272858686755], 'lng': [50.33231051081023, 30.368480777750914]}], 'dropped_nodes': [{'lat': 50.534377970341886, 'lng': 30.73514947892279}]}
            }

            {showResult ?
                Object.entries(result).map(([node, courierPoints]) => {
                    return (
                    courierPoints.map((points, count) => {
                        if (node === 'routes') {
                            return (
                        points.map((point, number) => {
                            if (node === 'routes' && number === 0) {
                            return (
                                <Marker
                                    lat={point.lat}
                                    lng={point.lng}
                                    text="Starting Point"
                                    startingPoint={true}
                                />
                            )
                        }
                        else if (number !== 0) {
                                return (
                                    <Marker
                                        lat={point.lat}
                                        lng={point.lng}
                                        text={`Courier ${count} number ${number}`}
                                        courier={count}
                                        deliveryNumber={number}
                                    />
                                )
                            }
                        return <></>

                        }))
                        }
                        else if (node === 'dropped_nodes') {
                            return (
                                <Marker
                                    // @ts-ignore
                                    lat={points.lat}
                                    // @ts-ignore
                                    lng={points.lng}
                                    text="Starting Point"
                                    startingPoint={true}
                                    droppedNode={true}
                                />
                            )
                        }
                        return <></>
                    // }
                    //     return <></>
                    }))
                    }) :
                points.map((point, count) => (
                  <Marker
                    lat={point.lat}
                    lng={point.lng}
                    text={`Point number ${count}`}
                    deliveryNumber={count}
                  />
              ))
            }
        </GoogleMapReact>
      </div>
    );
  }


export default SimpleMap;