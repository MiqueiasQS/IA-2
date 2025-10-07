const fs = require('fs');
const path = require('path');

// --- 1. PARÂMETROS DE CUSTO DEFINIDOS POR VOCÊ ---
const PRECO_KWH_ELETRICO = 1.00; // R$ 1,00 por kWh
const PRECO_COMBUSTIVEL_HIBRIDO = 6.00; // R$ 6,00 por litro de gasolina

// --- 2. TABELA DE REFERÊNCIA COM DADOS TÉCNICOS ---
// Dados baseados em fichas técnicas e no padrão PBEV/INMETRO.
const DADOS_TECNICOS_BYD = {
    'D1': {
        tipo: 'eletrico',
        bateriaKwh: 53.6,
        autonomiaKm: 270
    },
    'DOLPHIN MINI': {
        tipo: 'eletrico',
        bateriaKwh: 38,
        autonomiaKm: 280
    },
    'DOLPHIN': {
        tipo: 'eletrico',
        bateriaKwh: 44.9,
        autonomiaKm: 291
    },
    'ET3': {
        tipo: 'eletrico',
        bateriaKwh: 44.9,
        autonomiaKm: 170
    },
    'HAN': {
        tipo: 'eletrico',
        bateriaKwh: 85.4,
        autonomiaKm: 349
    },
    'SEAL': {
        tipo: 'eletrico',
        bateriaKwh: 82.5,
        autonomiaKm: 372
    },
    'TAN': {
        tipo: 'eletrico',
        bateriaKwh: 108.8,
        autonomiaKm: 309
    },
    'YUAN PLUS': {
        tipo: 'eletrico',
        bateriaKwh: 60.5,
        autonomiaKm: 294
    },
    'YUAN PRO': {
        tipo: 'eletrico',
        bateriaKwh: 47.5,
        autonomiaKm: 310
    },
    'KING': {
        tipo: 'hibrido',
        bateriaKwh: 8.3,
        autonomiaEletricaKm: 55,
        consumoGasolinaKmPorLitro: 25.6,
        tanqueLitros: 48
    },
    'SHARK': {
        tipo: 'hibrido',
        bateriaKwh: 29.6,
        autonomiaEletricaKm: 100,
        consumoGasolinaKmPorLitro: 10.5, // Estimativa
        tanqueLitros: 50
    },
    'SONG PLUS': {
        tipo: 'hibrido',
        bateriaKwh: 18.3,
        autonomiaEletricaKm: 78,
        consumoGasolinaKmPorLitro: 15.1,
        tanqueLitros: 52
    },
    'SONG PRO': {
        tipo: 'hibrido',
        bateriaKwh: 12.9,
        autonomiaEletricaKm: 51,
        consumoGasolinaKmPorLitro: 16.5,
        tanqueLitros: 52
    }
};

function enriquecerDataset() {
    const arquivoEntrada = 'dataset_byd_fipe.json';
    const arquivoSaida = 'dataset_byd_completo_custos.json';

    console.log(`Lendo o arquivo de entrada: ${arquivoEntrada}...`);

    try {
        const dadosRaw = fs.readFileSync(path.join(__dirname, arquivoEntrada), 'utf8');
        const veiculos = JSON.parse(dadosRaw);
        console.log(`Arquivo lido com sucesso. ${veiculos.length} veículos encontrados.`);

        const dadosEnriquecidos = veiculos.map(veiculo => {
            const modeloFipe = veiculo.Modelo.toUpperCase();
            let dadosTecnicosEncontrados = null;
            let chaveModeloEncontrada = null;

            // Procura o modelo da nossa tabela no nome do modelo da FIPE
            for (const chaveModelo in DADOS_TECNICOS_BYD) {
                if (modeloFipe.includes(chaveModelo)) {
                    dadosTecnicosEncontrados = DADOS_TECNICOS_BYD[chaveModelo];
                    chaveModeloEncontrada = chaveModelo;
                    break;
                }
            }

            const veiculoEnriquecido = { ...veiculo };

            if (dadosTecnicosEncontrados) {
                veiculoEnriquecido.ModeloBase = chaveModeloEncontrada;
                veiculoEnriquecido.TipoVeiculo = dadosTecnicosEncontrados.tipo;

                if (dadosTecnicosEncontrados.tipo === 'eletrico') {
                    const { bateriaKwh, autonomiaKm } = dadosTecnicosEncontrados;
                    const custoCarga = bateriaKwh * PRECO_KWH_ELETRICO;
                    const custoPorKm = custoCarga / autonomiaKm;

                    veiculoEnriquecido.CapacidadeBateriaKWH = bateriaKwh;
                    veiculoEnriquecido.AutonomiaTotalKM = autonomiaKm;
                    veiculoEnriquecido.CustoMedioPorKM_R$ = parseFloat(custoPorKm.toFixed(4));

                } else if (dadosTecnicosEncontrados.tipo === 'hibrido') {
                    const { bateriaKwh, autonomiaEletricaKm, consumoGasolinaKmPorLitro, tanqueLitros } = dadosTecnicosEncontrados;

                    const autonomiaTanque = tanqueLitros * consumoGasolinaKmPorLitro;
                    const autonomiaTotal = autonomiaEletricaKm + autonomiaTanque;

                    const custoCarga = bateriaKwh * PRECO_KWH_ELETRICO;
                    const custoTanque = tanqueLitros * PRECO_COMBUSTIVEL_HIBRIDO;
                    const custoTotal = custoCarga + custoTanque;
                    const custoPorKm = custoTotal / autonomiaTotal;

                    veiculoEnriquecido.CapacidadeBateriaKWH = bateriaKwh;
                    veiculoEnriquecido.AutonomiaEletricaKM = autonomiaEletricaKm;
                    veiculoEnriquecido.AutonomiaTotalKM = parseFloat(autonomiaTotal.toFixed(2));
                    veiculoEnriquecido.CustoMedioPorKM_R$ = parseFloat(custoPorKm.toFixed(4));
                }
            } else {
                veiculoEnriquecido.ModeloBase = 'N/A';
                veiculoEnriquecido.TipoVeiculo = 'N/A';
                veiculoEnriquecido.CustoMedioPorKM_R$ = 'N/A';
            }

            return veiculoEnriquecido;
        });

        fs.writeFileSync(path.join(__dirname, arquivoSaida), JSON.stringify(dadosEnriquecidos, null, 2), 'utf8');
        console.log(`\nProcesso finalizado com sucesso!`);
        console.log(`Arquivo enriquecido salvo como: ${arquivoSaida}`);

    } catch (error) {
        console.error(`\nOcorreu um erro: ${error.message}`);
        if (error.code === 'ENOENT') {
            console.error(`Certifique-se que o arquivo "${arquivoEntrada}" está na mesma pasta que o script.`);
        }
    }
}

enriquecerDataset();