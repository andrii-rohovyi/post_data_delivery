import React, {Component, useState} from 'react';
import GoogleMapReact from 'google-map-react';

const AnyReactComponent = ({ text }: any) => <div>{text}</div>;

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
      <div style={{ height: '100vh', width: '70%', float: "right" }}>
        <GoogleMapReact
          bootstrapURLKeys={{ key: "AIzaSyCWYtTeal3a9ttpSA8HYHmgJ21k4gnVMOA" }}
          defaultCenter={center}
          defaultZoom={11}
          onClick={addMapPoint}
        >
            {console.log(result, 'result')}
            {showResult ?
                result.map((courierPoints, count) => (
                    courierPoints.map((point, number) => (
                        <AnyReactComponent
                          lat={point.lat}
                          lng={point.lng}
                          text={`Courier ${count} number ${number}`}
                        />
                    ))
              )) :
                points.map((point, count) => (
                  <AnyReactComponent
                    lat={point.lat}
                    lng={point.lng}
                    text={`Point number ${count}`}
                  />
              ))
            }
        </GoogleMapReact>
      </div>
    );
  }


export default SimpleMap;