import React, {Component, useState} from 'react';
import GoogleMapReact from 'google-map-react';

type MarkerProps = {
    children?: React.ReactNode,
    lat: number
    lng: number
    text: string
    courier?: number
    deliveryNumber?: number,
    startingPoint?: boolean
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
   startingPoint
}) => (
    <>
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
    </>
);
type PointType = {
  lat: number,
  lng: number
}

type Props = {
    points: PointType[],
    addPoint: (points: PointType[]) => void,
    result: PointType[][],
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
            {showResult ?
                result.map((courierPoints, count) => {
                    return (
                    courierPoints.map((point, number) => {
                        if (count === 0 && number === 0) {
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
                            )}
                        return <></>
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