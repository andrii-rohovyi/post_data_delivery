import React from "react";
import {AddPointForm} from "./AddPointForm";

var moment = require('moment');

type PointType = {
  lat: number,
  lng: number,
  demand?: number
  time_window?: [moment.Moment, moment.Moment]
}

type Response = {
    routes: RouteType[],
    dropped_nodes: PointType[]
}


type RouteType = {
    route: PointType[],
    detailed_route: PointType[]
}


type Props = {
    points: PointType[],
    addPoint: (points: PointType[]) => void,
    result: Response,
    setResult: (points: Response) => void
    setShowResult: (showResult: boolean) => void
    maps: any
}

export const AddPointComponent: React.FC<Props> = ({
   points,
   addPoint,
   result,
   setResult,
   setShowResult,
    maps
}) => {
    return (
        <aside style={{ float: "left", width: "34%" }}>
        <AddPointForm
            points={points}
            addPoint={addPoint}
            result={result}
            setResult={setResult}
            setShowResult={setShowResult}
            maps={maps}
        />
      </aside>
    )
}