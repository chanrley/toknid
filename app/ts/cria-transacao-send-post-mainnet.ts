import { 
  Connection, 
  PublicKey, 
  SystemProgram, 
  Transaction, 
  sendAndConfirmTransaction,
  LAMPORTS_PER_SOL,
  Keypair
} from "@solana/web3.js";
import bs58 from "bs58";

/**
 * Cria e envia uma transação de envio de SOL na rede principal (Mainnet) - VALORES REAIS
 * @param chavePrivadaBase58 - Chave privada em formato base58
 * @param carteiraDestino - Chave pública da carteira de destino
 * @param valorMinimo - Se true, usa 1 lamport (valor mínimo), senão usa o valor informado ou do config
 * @param valorSOL - Valor em SOL (usado apenas se valorMinimo for false, opcional - usa config se não informado)
 * @returns Signature da transação enviada
 */
async function criaEEnviaTransacaoSendMainnet(
  chavePrivadaBase58: string,
  carteiraDestino: string,
  valorMinimo: boolean = true,
  valorSOL?: number
): Promise<string> {
  // ⚠️ CONEXÃO COM A REDE PRINCIPAL (MAINNET) - VALORES REAIS
  const connection = new Connection("https://api.mainnet-beta.solana.com", "confirmed");
  
  // Valor mínimo em Solana é 1 lamport = 0.000000001 SOL
  const valorMinimoLamports = 1;
  
  // Validar e decodificar a chave privada
  if (!chavePrivadaBase58 || chavePrivadaBase58.trim().length === 0) {
    throw new Error("Chave privada inválida ou vazia");
  }
  
  let secretKey: Uint8Array;
  try {
    secretKey = bs58.decode(chavePrivadaBase58);
    if (secretKey.length !== 64) {
      throw new Error("Chave privada deve ter 64 bytes (formato base58)");
    }
  } catch (error: any) {
    throw new Error(`Erro ao decodificar chave privada: ${error.message}`);
  }
  
  const keypair = Keypair.fromSecretKey(secretKey);
  const fromPublicKey = keypair.publicKey;
  
  // Validar carteira destino
  let toPublicKey: PublicKey;
  try {
    toPublicKey = new PublicKey(carteiraDestino);
  } catch (error: any) {
    throw new Error(`Carteira destino inválida: ${error.message}`);
  }
  
  // Verificar saldo da conta origem
  const balance = await connection.getBalance(fromPublicKey);
  if (balance === 0) {
    throw new Error("Conta origem não possui saldo suficiente");
  }
  
  // Verificar se a conta destino existe
  const accountInfo = await connection.getAccountInfo(toPublicKey);
  const contaExiste = accountInfo !== null;
  
  // Se usar valor mínimo e a conta não existe, precisa enviar rent mínimo
  // Rent mínimo em Solana é aproximadamente 890,880 lamports (0.00089 SOL)
  const RENT_EXEMPT_MINIMUM = 890880;
  
  let valorLamports: number;
  if (valorMinimo) {
    if (contaExiste) {
      valorLamports = valorMinimoLamports; // 1 lamport se a conta já existe
    } else {
      valorLamports = RENT_EXEMPT_MINIMUM + 1; // Rent mínimo + 1 lamport se a conta não existe
    }
  } else {
    // Usar valor do parâmetro (obrigatório quando valorMinimo é false)
    if (valorSOL === undefined || valorSOL <= 0) {
      throw new Error("Valor em SOL deve ser fornecido e maior que 0 quando valorMinimo for false");
    }
    valorLamports = Math.floor(valorSOL * LAMPORTS_PER_SOL);
  }
  
  // Verificar se há saldo suficiente (incluindo taxa de transação ~5000 lamports)
  const taxaEstimada = 5000;
  const saldoNecessario = valorLamports + taxaEstimada;
  if (balance < saldoNecessario) {
    throw new Error(`Saldo insuficiente. Necessário: ${saldoNecessario / LAMPORTS_PER_SOL} SOL, Disponível: ${balance / LAMPORTS_PER_SOL} SOL`);
  }
  
  // Obter o recent blockhash
  const { blockhash, lastValidBlockHeight } = await connection.getLatestBlockhash("confirmed");
  
  // Criar a transação
  const transaction = new Transaction({
    feePayer: fromPublicKey,
    recentBlockhash: blockhash,
  }).add(
    SystemProgram.transfer({
      fromPubkey: fromPublicKey,
      toPubkey: toPublicKey,
      lamports: valorLamports,
    })
  );
  
  // Assinar a transação
  transaction.sign(keypair);
  
  // Verificar se a transação está assinada
  if (!transaction.signature) {
    throw new Error("Falha ao assinar a transação");
  }
  
  // Enviar e confirmar a transação
  const signature = await sendAndConfirmTransaction(
    connection,
    transaction,
    [keypair],
    {
      commitment: "confirmed",
      maxRetries: 3,
    }
  );
  
  // Verificar se a transação foi confirmada
  const status = await connection.getSignatureStatus(signature);
  if (!status || !status.value || status.value.err) {
    throw new Error(`Transação falhou: ${status?.value?.err || "Status desconhecido"}`);
  }
  
  return signature;
}

export { criaEEnviaTransacaoSendMainnet };

