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

const route = {"type": "LineString", "coordinates": [[30.52077, 50.44368], [30.52079, 50.44374], [30.52095, 50.44423], [30.52113, 50.44479], [30.52117, 50.44489], [30.52193, 50.44724], [30.52209, 50.44775], [30.52225, 50.44819], [30.52247, 50.44863], [30.52282, 50.44907], [30.52288, 50.44913], [30.52307, 50.44933], [30.52321, 50.44946], [30.52339, 50.4496], [30.524, 50.45005], [30.52449, 50.45038], [30.52444, 50.45042], [30.52295, 50.45122], [30.52277, 50.4513], [30.5226, 50.45139], [30.52256, 50.4514], [30.52246, 50.4515], [30.52239, 50.45174], [30.5223, 50.45207], [30.52222, 50.45236], [30.5222, 50.45241], [30.52208, 50.45277], [30.522, 50.45302], [30.52199, 50.45305], [30.5219, 50.45327], [30.52179, 50.45348], [30.52168, 50.45364], [30.52162, 50.45372], [30.52159, 50.45377], [30.52128, 50.45419], [30.5211, 50.45442], [30.52107, 50.45447], [30.52098, 50.45459], [30.52063, 50.45501], [30.52052, 50.45508], [30.52038, 50.45516], [30.52016, 50.45522], [30.51997, 50.45526], [30.5199, 50.45527], [30.51972, 50.45535], [30.51913, 50.45538], [30.51901, 50.45533], [30.51735, 50.4554], [30.51712, 50.45541], [30.51694, 50.45541], [30.51636, 50.45541], [30.51586, 50.45541], [30.51446, 50.45543], [30.51393, 50.45541], [30.51379, 50.45541], [30.51366, 50.4554], [30.51304, 50.45537], [30.51288, 50.45536], [30.51238, 50.45537], [30.51181, 50.45534], [30.5117, 50.45534], [30.51165, 50.45533], [30.5116, 50.45533], [30.50869, 50.45517], [30.50811, 50.45517], [30.50759, 50.45524], [30.5074, 50.45526], [30.5071, 50.45522], [30.50649, 50.45529], [30.50638, 50.45531], [30.50613, 50.45534], [30.50576, 50.45543], [30.50486, 50.45567], [30.50476, 50.4557], [30.50482, 50.45579], [30.50556, 50.45688], [30.5056, 50.45695], [30.50568, 50.45707], [30.50582, 50.45726], [30.50586, 50.45731], [30.50594, 50.45742], [30.50597, 50.45747], [30.50599, 50.4575], [30.50606, 50.45762], [30.50623, 50.45791], [30.50629, 50.45801], [30.50637, 50.45815], [30.50639, 50.45831], [30.50635, 50.45889], [30.50632, 50.45948], [30.50626, 50.45964], [30.50617, 50.45978], [30.50603, 50.45991], [30.50602, 50.45992], [30.50601, 50.45993], [30.50593, 50.45997], [30.50578, 50.46003], [30.50546, 50.46014], [30.50514, 50.46027], [30.50493, 50.46043], [30.50461, 50.46077], [30.50458, 50.46085], [30.50456, 50.461], [30.50462, 50.46111], [30.50468, 50.46121], [30.50502, 50.46166], [30.5053, 50.46198], [30.50555, 50.46213], [30.50622, 50.46245], [30.5065, 50.46259], [30.50656, 50.46262], [30.50668, 50.46268], [30.50684, 50.46265], [30.50705, 50.46252], [30.50706, 50.46252], [30.50745, 50.46277], [30.50754, 50.46282], [30.50849, 50.4634], [30.509, 50.46373], [30.50965, 50.46416], [30.51023, 50.46454], [30.51026, 50.46456], [30.51052, 50.46472], [30.5109, 50.46497], [30.51098, 50.46502], [30.51106, 50.46507], [30.51109, 50.46509], [30.5113, 50.46523], [30.51137, 50.46528], [30.51289, 50.46631], [30.51289, 50.46631], [30.51335, 50.46661], [30.51338, 50.46662], [30.51454, 50.46738], [30.51459, 50.46742], [30.51461, 50.46743], [30.51505, 50.46771], [30.51536, 50.46792], [30.51574, 50.46817], [30.51612, 50.46841], [30.51673, 50.46882], [30.5168, 50.46886], [30.5169, 50.46893], [30.51787, 50.46956], [30.51838, 50.46988], [30.51844, 50.46993], [30.51851, 50.46997], [30.51962, 50.4707], [30.52048, 50.47126], [30.52052, 50.47129], [30.52069, 50.4714], [30.52079, 50.47134], [30.52188, 50.47068], [30.522, 50.47061], [30.52332, 50.46979], [30.52334, 50.46977], [30.52341, 50.46973], [30.52364, 50.46956], [30.52383, 50.46943], [30.52389, 50.46939], [30.52403, 50.46926], [30.52414, 50.46908], [30.52437, 50.4681], [30.52455, 50.46746], [30.52459, 50.46732], [30.52462, 50.46713], [30.52481, 50.46636], [30.52519, 50.46456], [30.52534, 50.46385], [30.52544, 50.4633], [30.52585, 50.46139], [30.52604, 50.46052], [30.52597, 50.46031], [30.52591, 50.46025], [30.52543, 50.45997], [30.52451, 50.45941], [30.52445, 50.45937], [30.5244, 50.45935], [30.52466, 50.45918]]};


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
                    background: startingPoint ? "#006DFF" : courier ? colors[courier] : "#900020",
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

// type Response = {
//     routes: PointType[][],
//     dropped_nodes: PointType[][]
// }

type Response = {
    routes: RouteType[],
    dropped_nodes: PointType[]
}


type RouteType = {
    route: PointType[],
    detailed_route: PointType[]
}

const resp: Response = {
    'routes': [
        {
            'route': [
                {
                    'lat': 50.44368,
                    'lng': 30.52077
                },
                {
                    'lat': 50.45918,
                    'lng': 30.52466
                },
            ],
            'detailed_route': route.coordinates.map((coordinate => {
            return(
            {
                lat: coordinate[1],
                lng: coordinate[0]
            }
            )
        }))
        },
        {
            'route': [
                {
                    'lat': 50.36254421120163,
                    'lng': 30.647584993775194
                },
                {
                    'lat': 50.461872909975,
                    'lng': 30.703203279908006
                },
            ],
            'detailed_route': [
                {
                    'lat': 50.461872909975,
                    'lng': 30.703203279908006
                },
                {
                    'lat': 50.461872909975,
                    'lng': 30.703203279908006
                },
            ]
        }
    ],
    'dropped_nodes': [
        {
            'lat': 50.461872909975,
            'lng': 30.703203279908006
        },
        {
            'lat': 50.461872909975,
            'lng': 30.703203279908006
        },
    ]
}

type Props = {
    points: PointType[],
    addPoint: (points: PointType[]) => void,
    result: Response,
    showResult: boolean,
    setMap: (map: any) => void
}

export const SimpleMap: React.FC<Props> = ({
   points,
   addPoint,
   result,
   showResult,
   setMap
}) => {

    const center = {
      lat: 50.45466,
      lng: 30.5238
    }

    const handleApiLoaded = (map: any, maps: any) => {
        const res = route.coordinates.map((coordinate => {
            return(
            {
                lat: coordinate[1],
                lng: coordinate[0]
            }
            )
        }))
        console.log(res, 'coordinates');
        const flightPlanCoordinates = [
        { lat: 37.772, lng: -122.214 },
        { lat: 21.291, lng: -157.821 },
        { lat: -18.142, lng: 178.431 },
        { lat: -27.467, lng: 153.027 },
      ];
      const flightPath = new maps.Polyline({
        path: res,
        geodesic: true,
        strokeColor: "#FF0000",
        strokeOpacity: 1.0,
        strokeWeight: 2,
      });
      setMap({maps, map});
      // flightPath.setMap(map);


    };


    const addMapPoint = (event: PointType) => {
      addPoint(points.concat([{lat: event.lat, lng: event.lng}]))
    }
    return (
      // Important! Always set the container height explicitly
      <div style={{ height: '100vh', width: '66%', float: "right" }}>
        <GoogleMapReact
          bootstrapURLKeys={{ key: "AIzaSyCWYtTeal3a9ttpSA8HYHmgJ21k4gnVMOA" }}
          defaultCenter={center}
          defaultZoom={11}
          onClick={addMapPoint}
          options={{styles: [{ stylers: [{ 'saturation': -100 }, ] }]}}
          yesIWantToUseGoogleMapApiInternals={true}
          onGoogleApiLoaded={({ map, maps }) => handleApiLoaded(map, maps)}
        >
            {showResult &&
                result.dropped_nodes.map((droppedNode) => (
                    <Marker
                        lat={droppedNode.lat}
                        lng={droppedNode.lng}
                        text="Starting Point"
                        droppedNode={true}
                    />
                ))
            }
            {showResult ?
                result.routes.map((courierPoints, courierNumber) => {
                    return (
                    courierPoints.route.map((point, count) => {
                            if (count === 0) {
                                return (
                                    <Marker
                                        lat={point.lat}
                                        lng={point.lng}
                                        text="Starting Point"
                                        startingPoint={true}
                                    />
                                )
                            }
                            return (
                                <Marker
                                    lat={point.lat}
                                    lng={point.lng}
                                    text={`Courier ${count} number ${courierNumber}`}
                                    courier={count}
                                    deliveryNumber={courierNumber}
                                />
                            )
                    }
                    ))
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