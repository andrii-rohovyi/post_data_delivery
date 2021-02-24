import React, {useState} from 'react';
import './App.css';
import "antd/dist/antd.css";
import SimpleMap from "./components/SimpleMap";
import {AddPointComponent} from "./components/AddPointComponent";

type PointType = {
  lat: number,
  lng: number,
  demand?: number
  time_window?: [Date, Date]
}

type Response = {
    routes: PointType[][],
    dropped_nodes: PointType[][]
}

function App() {
  const [points, addPoint] = useState<PointType[]>([{
  lat: 50.4486941427873,
  lng: 30.52272858686755
  }]);
  const [result, setResult] = useState<Response>({routes: [], dropped_nodes: []});
  const [showResult, setShowResult] = useState(false);
  return (
    <div className="App">
        <AddPointComponent
            points={points}
            addPoint={addPoint}
            result={result}
            setResult={setResult}
            setShowResult={setShowResult}
        />
      <div>
        <SimpleMap points={points} addPoint={addPoint} result={result} showResult={showResult}/>
      </div>
    </div>
  );
}

export default App;
