import React from "react";
import {AddPointForm} from "./AddPointForm";

type PointType = {
  lat: number,
  lng: number,
  demand?: number
  time_window?: [Date, Date]
}

type Props = {
    points: PointType[],
    addPoint: (points: PointType[]) => void,
    result: PointType[][],
    setResult: (points: PointType[][]) => void
    setShowResult: (showResult: boolean) => void
}

export const AddPointComponent: React.FC<Props> = ({
   points,
   addPoint,
   result,
   setResult,
   setShowResult
}) => {
    return (
        <aside style={{ float: "left", width: "40%" }}>
        <AddPointForm
            points={points}
            addPoint={addPoint}
            result={result}
            setResult={setResult}
            setShowResult={setShowResult}
        />
      </aside>
    )
}