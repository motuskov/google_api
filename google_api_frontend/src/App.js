import { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import Graph from './Graph';
import OrderItems from './OrderItems.js';
import Total from './Total.js';

export default function App() {
  const serverUrl = 'http://localhost:8000/api/order-items';
  const updateInterval = 5000;
  const [data, setData] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
        const response = await axios.get(serverUrl);
        setData(response.data);
    };

    fetchData();

    const intervalId = setInterval(() => {
        fetchData();
    }, updateInterval);

    return () => clearInterval(intervalId);
  }, [serverUrl]);

  return (
    <div className='App'>
      <div className='App-header'>
        <img className='App-logo' src='logo.png' />
      </div>
      <div className='App-container'>
        <div className='App-graph'>
          <Graph data={data} />
        </div>
        <div className='App-data'>
          <div className='App-total'>
            <Total data={data} />
          </div>
          <div className='App-items'>
            <OrderItems data={data} />
          </div>
        </div>
      </div>
    </div>
  )
}
