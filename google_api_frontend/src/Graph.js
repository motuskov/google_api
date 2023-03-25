import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

export default function Graph(props) {
  const maxCostUsd = Math.max(...props.data.map(obj => parseFloat(obj.cost_usd)));

  return (
    <div>
      <BarChart width={700} height={500} data={props.data}>
        <CartesianGrid strokeDasharray='3 3' />
        <XAxis dataKey='delivery_date' />
        <YAxis domain={[0, maxCostUsd]} />
        <Tooltip />
        <Legend />
        <Bar dataKey='cost_usd' fill='#8884d8' />
      </BarChart>
    </div>
  );
};
  