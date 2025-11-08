"""
LaniakeA Protocol - 8D Hypercube Visualizer
Visualizes the 8-dimensional hypercube blockchain in lower dimensions
"""

import numpy as np
import json
import logging
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime

logger = logging.getLogger("HypercubeVisualizer")


class HypercubeVisualizer:
    """
    Visualizes 8-dimensional hypercube by projecting to 2D/3D
    """
    
    def __init__(self):
        """Initialize hypercube visualizer"""
        self.dimensions = 8
        self.vertices = self._generate_hypercube_vertices()
        self.edges = self._generate_hypercube_edges()
        
        logger.info(f"✅ Hypercube visualizer initialized")
        logger.info(f"   Vertices: {len(self.vertices)}")
        logger.info(f"   Edges: {len(self.edges)}")
    
    def _generate_hypercube_vertices(self) -> np.ndarray:
        """
        Generate all vertices of an 8D hypercube
        
        Returns:
            Array of shape (256, 8) containing all vertices
        """
        # 8D hypercube has 2^8 = 256 vertices
        n_vertices = 2 ** self.dimensions
        vertices = np.zeros((n_vertices, self.dimensions))
        
        for i in range(n_vertices):
            for d in range(self.dimensions):
                # Each vertex coordinate is either 0 or 1
                vertices[i, d] = (i >> d) & 1
        
        # Center at origin and scale to [-1, 1]
        vertices = (vertices - 0.5) * 2
        
        return vertices
    
    def _generate_hypercube_edges(self) -> List[Tuple[int, int]]:
        """
        Generate edges connecting hypercube vertices
        
        Returns:
            List of (vertex_i, vertex_j) tuples
        """
        edges = []
        n_vertices = len(self.vertices)
        
        for i in range(n_vertices):
            for j in range(i + 1, n_vertices):
                # Two vertices are connected if they differ in exactly one dimension
                diff = np.abs(self.vertices[i] - self.vertices[j])
                if np.sum(diff > 0) == 1:
                    edges.append((i, j))
        
        return edges
    
    def project_to_3d(self, rotation_matrix: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Project 8D hypercube to 3D using rotation
        
        Args:
            rotation_matrix: Optional 3x8 rotation matrix
            
        Returns:
            Array of shape (256, 3) containing 3D projections
        """
        if rotation_matrix is None:
            # Default projection: use first 3 dimensions with some mixing
            rotation_matrix = np.array([
                [1, 0.3, 0.1, 0, 0.2, 0, 0, 0.1],
                [0, 0.7, 0.2, 0.3, 0, 0.1, 0, 0],
                [0, 0, 0.7, 0.4, 0.1, 0.2, 0.3, 0]
            ])
            # Normalize rows
            rotation_matrix = rotation_matrix / np.linalg.norm(rotation_matrix, axis=1, keepdims=True)
        
        projected = self.vertices @ rotation_matrix.T
        return projected
    
    def project_to_2d(self, rotation_matrix: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Project 8D hypercube to 2D
        
        Args:
            rotation_matrix: Optional 2x8 rotation matrix
            
        Returns:
            Array of shape (256, 2) containing 2D projections
        """
        if rotation_matrix is None:
            # Default projection
            rotation_matrix = np.array([
                [1, 0.5, 0.3, 0.2, 0.1, 0, 0, 0],
                [0, 0.5, 0.7, 0.4, 0.3, 0.2, 0.1, 0]
            ])
            rotation_matrix = rotation_matrix / np.linalg.norm(rotation_matrix, axis=1, keepdims=True)
        
        projected = self.vertices @ rotation_matrix.T
        return projected
    
    def get_block_position_8d(self, block_index: int) -> np.ndarray:
        """
        Get 8D position for a block in the hypercube
        
        Args:
            block_index: Block index in blockchain
            
        Returns:
            8D coordinate array
        """
        # Map block index to hypercube position
        # Use modulo to wrap around hypercube
        vertex_index = block_index % len(self.vertices)
        
        # Add some variation based on block properties
        position = self.vertices[vertex_index].copy()
        
        # Add small perturbation to distinguish blocks at same vertex
        perturbation = np.random.RandomState(block_index).randn(8) * 0.1
        position += perturbation
        
        return position
    
    def visualize_blockchain_3d(self, blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create 3D visualization data for blockchain
        
        Args:
            blocks: List of block dictionaries
            
        Returns:
            Visualization data dictionary
        """
        # Get 3D positions for all blocks
        block_positions_8d = []
        for i, block in enumerate(blocks):
            pos_8d = self.get_block_position_8d(i)
            block_positions_8d.append(pos_8d)
        
        # Project to 3D
        positions_8d = np.array(block_positions_8d)
        
        # Create rotation matrix that emphasizes interesting dimensions
        rotation_matrix = np.array([
            [0.7, 0.3, 0.2, 0.1, 0.1, 0, 0, 0],
            [0.2, 0.6, 0.4, 0.2, 0, 0.1, 0, 0],
            [0.1, 0.1, 0.4, 0.7, 0.2, 0.1, 0.1, 0]
        ])
        rotation_matrix = rotation_matrix / np.linalg.norm(rotation_matrix, axis=1, keepdims=True)
        
        positions_3d = positions_8d @ rotation_matrix.T
        
        # Create visualization data
        viz_data = {
            'blocks': [],
            'connections': [],
            'hypercube_structure': {
                'vertices_3d': self.project_to_3d(rotation_matrix).tolist(),
                'edges': self.edges
            }
        }
        
        # Add block data
        for i, (block, pos_3d) in enumerate(zip(blocks, positions_3d)):
            viz_data['blocks'].append({
                'index': i,
                'hash': block.get('hash', f'block_{i}')[:16],
                'position': pos_3d.tolist(),
                'timestamp': block.get('timestamp', 0),
                'transactions': block.get('transactions_count', 0)
            })
        
        # Add connections between consecutive blocks
        for i in range(len(blocks) - 1):
            viz_data['connections'].append({
                'from': i,
                'to': i + 1,
                'from_pos': positions_3d[i].tolist(),
                'to_pos': positions_3d[i + 1].tolist()
            })
        
        return viz_data
    
    def generate_plotly_3d(self, blocks: List[Dict[str, Any]]) -> str:
        """
        Generate Plotly 3D visualization HTML
        
        Args:
            blocks: List of block dictionaries
            
        Returns:
            HTML string with Plotly visualization
        """
        viz_data = self.visualize_blockchain_3d(blocks)
        
        # Create Plotly data
        plotly_data = []
        
        # Add hypercube structure (faint)
        hypercube_vertices = np.array(viz_data['hypercube_structure']['vertices_3d'])
        
        # Add hypercube edges
        edge_x, edge_y, edge_z = [], [], []
        for edge in viz_data['hypercube_structure']['edges'][:100]:  # Limit edges for clarity
            v1, v2 = edge
            edge_x.extend([hypercube_vertices[v1][0], hypercube_vertices[v2][0], None])
            edge_y.extend([hypercube_vertices[v1][1], hypercube_vertices[v2][1], None])
            edge_z.extend([hypercube_vertices[v1][2], hypercube_vertices[v2][2], None])
        
        # Add blocks
        block_x = [b['position'][0] for b in viz_data['blocks']]
        block_y = [b['position'][1] for b in viz_data['blocks']]
        block_z = [b['position'][2] for b in viz_data['blocks']]
        block_text = [f"Block {b['index']}<br>Hash: {b['hash']}<br>Txs: {b['transactions']}" 
                     for b in viz_data['blocks']]
        
        # Add connections
        conn_x, conn_y, conn_z = [], [], []
        for conn in viz_data['connections']:
            conn_x.extend([conn['from_pos'][0], conn['to_pos'][0], None])
            conn_y.extend([conn['from_pos'][1], conn['to_pos'][1], None])
            conn_z.extend([conn['from_pos'][2], conn['to_pos'][2], None])
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        body {{ margin: 0; padding: 20px; background: #0a0a0a; color: #fff; font-family: Arial; }}
        #plot {{ width: 100%; height: 90vh; }}
        h1 {{ text-align: center; color: #00d4ff; }}
    </style>
</head>
<body>
    <h1>🌌 LaniakeA Protocol - 8D Hypercube Blockchain Visualization</h1>
    <div id="plot"></div>
    <script>
        var hypercubeEdges = {{
            type: 'scatter3d',
            mode: 'lines',
            x: {edge_x},
            y: {edge_y},
            z: {edge_z},
            line: {{ color: 'rgba(100, 100, 150, 0.2)', width: 1 }},
            hoverinfo: 'skip',
            name: 'Hypercube Structure'
        }};
        
        var blockConnections = {{
            type: 'scatter3d',
            mode: 'lines',
            x: {conn_x},
            y: {conn_y},
            z: {conn_z},
            line: {{ color: 'rgba(0, 212, 255, 0.6)', width: 3 }},
            hoverinfo: 'skip',
            name: 'Blockchain'
        }};
        
        var blocks = {{
            type: 'scatter3d',
            mode: 'markers+text',
            x: {block_x},
            y: {block_y},
            z: {block_z},
            text: {[f"B{b['index']}" for b in viz_data['blocks']]},
            hovertext: {block_text},
            marker: {{
                size: 8,
                color: {list(range(len(viz_data['blocks'])))},
                colorscale: 'Viridis',
                showscale: true,
                colorbar: {{ title: 'Block Index' }}
            }},
            textposition: 'top center',
            textfont: {{ size: 8, color: 'white' }},
            name: 'Blocks'
        }};
        
        var layout = {{
            scene: {{
                xaxis: {{ title: 'X', backgroundcolor: 'rgb(10, 10, 10)', gridcolor: 'rgb(50, 50, 50)' }},
                yaxis: {{ title: 'Y', backgroundcolor: 'rgb(10, 10, 10)', gridcolor: 'rgb(50, 50, 50)' }},
                zaxis: {{ title: 'Z', backgroundcolor: 'rgb(10, 10, 10)', gridcolor: 'rgb(50, 50, 50)' }},
                bgcolor: 'rgb(10, 10, 10)'
            }},
            paper_bgcolor: '#0a0a0a',
            plot_bgcolor: '#0a0a0a',
            showlegend: true,
            legend: {{ x: 0, y: 1 }}
        }};
        
        Plotly.newPlot('plot', [hypercubeEdges, blockConnections, blocks], layout);
    </script>
</body>
</html>
"""
        return html
    
    def save_visualization(self, blocks: List[Dict[str, Any]], filepath: str):
        """Save 3D visualization to HTML file"""
        try:
            html = self.generate_plotly_3d(blocks)
            with open(filepath, 'w') as f:
                f.write(html)
            logger.info(f"✅ Visualization saved to {filepath}")
        except Exception as e:
            logger.error(f"❌ Failed to save visualization: {e}")


# Example usage
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    # Create visualizer
    viz = HypercubeVisualizer()
    
    # Create sample blocks
    sample_blocks = []
    for i in range(20):
        sample_blocks.append({
            'hash': f'0x{i:064x}',
            'timestamp': 1700000000 + i * 600,
            'transactions_count': np.random.randint(1, 50)
        })
    
    # Generate visualization
    print("\n" + "="*60)
    print("Generating 8D Hypercube Visualization")
    print("="*60)
    
    viz.save_visualization(sample_blocks, '/tmp/laniakea_hypercube_viz.html')
    
    print("\n✅ Visualization generated!")
    print(f"   Open: /tmp/laniakea_hypercube_viz.html")
    print(f"   Blocks: {len(sample_blocks)}")
    print(f"   Hypercube vertices: {len(viz.vertices)}")
    print(f"   Hypercube edges: {len(viz.edges)}")
