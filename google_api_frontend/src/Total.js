import './Total.css';

export default function Total(props) {
  const total = props.data.reduce((acc, obj) => acc + parseFloat(obj.cost_usd), 0);

  return (
    <div className='Total'>
        <div className='Total-header'>
          Total
        </div>
        <div className='Total-value'>
          {total}
        </div>
    </div>
  )
}
