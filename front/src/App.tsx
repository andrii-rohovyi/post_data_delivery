import React, {useState} from 'react';
import './App.css';
import "antd/dist/antd.css";
import SimpleMap from "./components/SimpleMap";
import {AddPointComponent} from "./components/AddPointComponent";

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

function App() {
  const [points, addPoint] = useState<PointType[]>([{
  lat: 50.4486941427873,
  lng: 30.52272858686755
  }]);
  const [result, setResult] = useState<Response>({routes: [], dropped_nodes: []});
  const [showResult, setShowResult] = useState(false);
  const [maps, setMaps] = useState(null);
  return (
    <div className="App">
        <AddPointComponent
            points={points}
            addPoint={addPoint}
            result={result}
            setResult={setResult}
            setShowResult={setShowResult}
            maps={maps}
        />
      <div>
        <SimpleMap
            points={points}
            addPoint={addPoint}
            result={result}
            showResult={showResult}
            setMap={setMaps}
        />
      </div>
    </div>
  );
}

export default App;
