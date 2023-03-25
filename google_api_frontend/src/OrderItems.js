import './OrderItems.css';

export default function OrderItems(props) {

  return (
    <table className='OrderItems-table'>
      <thead>
        <tr>
          <th>№</th>
          <th>Заказ №</th>
          <th>Стоимость, $</th>
          <th>Стоимость, руб.</th>
          <th>Срок поставки</th>
        </tr>
      </thead>
      <tbody>
        {props.data.map(item => (
          <tr key={item.id}>
            <td>{item.id}</td>
            <td>{item.order_number}</td>
            <td>{item.cost_usd}</td>
            <td>{item.cost_rub}</td>
            <td>{item.delivery_date}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
