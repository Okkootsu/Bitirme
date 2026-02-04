import { BrowserRouter } from "react-router";
import { AppRouter } from "./routes";

function App() {
  return (
    <BrowserRouter>
      <AppRouter />
    </BrowserRouter>
  );
}

export default App;
