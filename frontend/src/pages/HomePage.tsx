import { useState } from 'react';
import { Button } from '@/components/Button';

export const HomePage = () => {
  const [count, setCount] = useState(0);

  return (
    <div className="flex-1 flex flex-col items-center justify-center bg-gray-50 space-y-6">
      
      <h1 className="text-4xl font-extrabold text-gray-800 tracking-tight">
        React + Tailwind CSS
      </h1>
      
      <p className="text-gray-500 text-lg">
        Test
      </p>


      <div className="flex gap-4">
        <Button onClick={() => setCount(count + 1)}>
          Arttır (+1)
        </Button>

        <Button variant="danger" onClick={() => setCount(0)}>
          Sıfırla
        </Button>
      </div>

      <div className="p-4 bg-white shadow-md rounded-xl border border-gray-200">
        <h2 className="text-2xl font-bold text-blue-600">
          Sayaç: {count}
        </h2>
      </div>
    </div>
  );
};