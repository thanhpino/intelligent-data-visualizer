'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import { Bar, Pie } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement);

const API_BASE_URL = 'https://my-data-api-4qlf.onrender.com';
export default function Home() {
    const [datasets, setDatasets] = useState([]);
    const [selectedDataset, setSelectedDataset] = useState(null);
    const [suggestions, setSuggestions] = useState([]);
    const [columns, setColumns] = useState([]);
    const [chartData, setChartData] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    useEffect(() => {
        axios.get(`${API_BASE_URL}/api/datasets`)
            .then(res => setDatasets(res.data))
            .catch(err => console.error("Error fetching datasets:", err));
    }, []);

    const handleDatasetSelect = async (datasetId) => {
        setIsLoading(true);
        setChartData(null);
        setSelectedDataset(datasetId);
        try {
            const res = await axios.get(`${API_BASE_URL}/api/datasets/${datasetId}/suggestions`);
            setSuggestions(res.data.suggestions);
            setColumns(res.data.columns);
        } catch (err) {
            console.error("Error fetching suggestions:", err);
        } finally {
            setIsLoading(false);
        }
    };

    const handleAnalysis = async (suggestion) => {
        setIsLoading(true);
        const groupByCol = columns.find(c => c !== suggestion.column);
        if (!groupByCol) {
            alert("Không tìm thấy cột phù hợp để gom nhóm!");
            setIsLoading(false);
            return;
        }
        try {
            const res = await axios.post(`${API_BASE_URL}/api/datasets/${selectedDataset}/analyze`, {
                type: suggestion.type,
                column: suggestion.column,
                group_by_col: groupByCol,
            });

            setChartData({
                type: res.data.chart_type,
                title: res.data.title,
                data: {
                    labels: res.data.labels,
                    datasets: [{
                        data: res.data.data,
                        backgroundColor: ['#34D399', '#F87171', '#60A5FA', '#FBBF24', '#A78BFA', '#F472B6'],
                        borderColor: '#1f2937',
                        borderWidth: 1,
                    }],
                },
            });
        } catch (err) {
            console.error("Error analyzing data:", err);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <main className="min-h-screen p-8 md:p-16 font-sans">
            {/* Banner */}
            <div className="text-center p-10 rounded-xl bg-gray-800/50 mb-12 border border-gray-700">
                <h1 className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-green-300 via-blue-400 to-purple-500">
                    Trực Quan Hóa Dữ Liệu Thông Minh
                </h1>
                <p className="text-gray-400 mt-4 text-lg">
                    Chọn một bộ dữ liệu, hệ thống sẽ tự động gợi ý các hướng phân tích cho bạn.
                </p>
            </div>

            {/* Grid layout */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Cột trái: Chọn Dataset và Gợi ý */}
                <div className="lg:col-span-1 space-y-8">
                    <div>
                        <h2 className="text-2xl font-semibold mb-4 border-b-2 border-green-400 pb-2">1. Chọn Dataset</h2>
                        <div className="space-y-3">
                            {datasets.map(ds => (
                                <button key={ds} onClick={() => handleDatasetSelect(ds)}
                                    className={`w-full text-left p-4 rounded-lg transition-all duration-200 ${selectedDataset === ds ? 'bg-green-500 shadow-lg' : 'bg-gray-700 hover:bg-gray-600'}`}>
                                    {ds.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                                </button>
                            ))}
                        </div>
                    </div>
                    {selectedDataset && (
                        <div>
                            <h2 className="text-2xl font-semibold mb-4 border-b-2 border-blue-400 pb-2">2. Chọn phân tích</h2>
                            <div className="space-y-3">
                                {suggestions.map(sug => (
                                    <button key={sug.id} onClick={() => handleAnalysis(sug)}
                                        className="w-full text-left p-4 bg-gray-700 hover:bg-gray-600 rounded-lg transition-all duration-200">
                                        {sug.text}
                                    </button>
                                ))}
                            </div>
                        </div>
                    )}
                </div>

                {/* Cột phải: Hiển thị kết quả */}
                <div className="lg:col-span-2 bg-gray-800/50 rounded-xl p-8 border border-gray-700 min-h-[400px] flex items-center justify-center">
                    {isLoading && <p>Đang phân tích...</p>}
                    {!isLoading && !chartData && <p className="text-gray-500">Kết quả phân tích sẽ hiển thị ở đây</p>}
                    {chartData && (
                        <div className="w-full">
                            <h3 className="text-xl font-semibold mb-4 text-center">{chartData.title}</h3>
                            {chartData.type === 'bar' && <Bar options={{ responsive: true }} data={chartData.data} />}
                            {chartData.type === 'pie' && <Pie options={{ responsive: true }} data={chartData.data} />}
                        </div>
                    )}
                </div>
            </div>
        </main>
    );
}