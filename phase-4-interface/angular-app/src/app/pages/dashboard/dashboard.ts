import { Component, signal, computed, effect, ViewChild, ElementRef, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { DataService } from '../../core/data';
import { 
  Kpi, 
  ConsumoDiario, 
  ConsumoSector, 
  Anomalia, 
  Recomendacion, 
  ApiResponse 
} from '../../core/models';

interface ChatMessage {
  id: string;
  text: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
}

interface ChatHistory {
  id: string;
  title: string;
  timestamp: Date;
  messages: ChatMessage[];
}

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css'
})
export class Dashboard implements AfterViewInit {
  @ViewChild('chatContainer') chatContainer!: ElementRef;

  // Signals for reactive state management
  readonly sedes = signal<string[]>([]);
  readonly selectedSede = signal<string>('');
  readonly kpis = signal<Kpi | null>(null);
  readonly consumoDiario = signal<ConsumoDiario[]>([]);
  readonly consumoSector = signal<ConsumoSector[]>([]);
  readonly anomalias = signal<Anomalia[]>([]);
  readonly recomendaciones = signal<Recomendacion[]>([]);
  readonly loading = signal<boolean>(false);
  readonly error = signal<string>('');

  // Chat signals - start empty, will be populated when user creates chats
  readonly chatHistories = signal<ChatHistory[]>([]);
  readonly currentChatId = signal<string | null>(null);
  readonly currentMessages = signal<ChatMessage[]>([]);
  readonly chatInput = signal<string>('');
  readonly isSending = signal<boolean>(false);

  constructor(private dataService: DataService) {
    // Initialize chat histories
    this.chatHistories.set([]);
    
    // Auto-scroll effect for new messages
    effect(() => {
      const messages = this.currentMessages();
      if (messages.length > 0) {
        setTimeout(() => this.scrollToBottom(), 100);
      }
    });
  }

  ngAfterViewInit(): void {
    // Called after the view is initialized
  }

  private scrollToBottom(): void {
    if (this.chatContainer && this.chatContainer.nativeElement) {
      const container = this.chatContainer.nativeElement;
      container.scrollTop = container.scrollHeight;
    }
  }

  ngOnInit(): void {
    this.loadInitialData();
  }

  loadInitialData(): void {
    this.loading.set(true);
    this.dataService.getSedes().subscribe({
      next: (sedes) => {
        this.sedes.set(sedes);
        if (sedes.length > 0) {
          this.selectedSede.set(sedes[0]);
          this.loadSedeData(sedes[0]);
        }
        this.loading.set(false);
      },
      error: (err) => {
        this.error.set('Error loading sedes: ' + err.message);
        this.loading.set(false);
      }
    });
  }

  onSedeChange(sede: string): void {
    this.selectedSede.set(sede);
    this.loadSedeData(sede);
  }

  loadSedeData(sede: string): void {
    this.loading.set(true);
    this.error.set('');

    // Load all data in parallel
    Promise.all([
      this.dataService.getKpis(sede).toPromise(),
      this.dataService.getConsumoDiario(sede).toPromise(),
      this.dataService.getConsumoSector(sede).toPromise(),
      this.dataService.getAnomalias(sede).toPromise(),
      this.dataService.getRecomendaciones(sede).toPromise()
    ]).then(([kpis, consumoDiario, consumoSector, anomalias, recomendaciones]) => {
      this.kpis.set(kpis || null);
      this.consumoDiario.set(consumoDiario || []);
      this.consumoSector.set(consumoSector || []);
      this.anomalias.set(anomalias?.data || []);
      this.recomendaciones.set(recomendaciones?.data || []);
      this.loading.set(false);
    }).catch((err) => {
      this.error.set('Error loading data: ' + err.message);
      this.loading.set(false);
    });
  }

  // Chat methods
  selectChat(chatId: string): void {
    const chat = this.chatHistories().find(c => c.id === chatId);
    if (chat) {
      this.currentChatId.set(chatId);
      this.currentMessages.set([...chat.messages]);
    }
  }

  createNewChat(): void {
    const newChat: ChatHistory = {
      id: Date.now().toString(),
      title: 'Nuevo chat',
      timestamp: new Date(),
      messages: []
    };
    this.chatHistories.set([newChat, ...this.chatHistories()]);
    this.currentChatId.set(newChat.id);
    this.currentMessages.set([]);
  }

  sendMessage(): void {
    const message = this.chatInput().trim();
    if (!message || this.isSending()) return;

    // If no chat is selected, create a new one
    if (!this.currentChatId()) {
      this.createNewChat();
    }

    this.isSending.set(true);

    // Create user message
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      text: message,
      sender: 'user',
      timestamp: new Date()
    };

    // Add to current messages
    this.currentMessages.set([...this.currentMessages(), userMessage]);
    this.chatInput.set('');

    // Call real API
    this.dataService.chat({ sede: this.selectedSede(), pregunta: message }).subscribe({
      next: (response) => {
        const aiMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          text: response.respuesta || 'No se pudo obtener una respuesta.',
          sender: 'assistant',
          timestamp: new Date()
        };
        
        this.currentMessages.set([...this.currentMessages(), aiMessage]);
        this.isSending.set(false);

        // Update chat history
        this.updateChatHistory();
      },
      error: (error) => {
        console.error('Chat API Error:', error);
        const errorMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          text: `Error: ${error.error?.message || 'No se pudo conectar con el asistente IA. Por favor, intenta nuevamente.'}`,
          sender: 'assistant',
          timestamp: new Date()
        };
        
        this.currentMessages.set([...this.currentMessages(), errorMessage]);
        this.isSending.set(false);

        // Update chat history
        this.updateChatHistory();
      }
    });
  }

  private updateChatHistory(): void {
    if (this.currentChatId()) {
      const histories = this.chatHistories();
      const index = histories.findIndex(c => c.id === this.currentChatId());
      if (index !== -1) {
        histories[index].messages = this.currentMessages();
        // Update title based on first user message
        if (histories[index].title === 'Nuevo chat' && this.currentMessages().length > 0) {
          const firstUserMessage = this.currentMessages().find(m => m.sender === 'user');
          if (firstUserMessage) {
            histories[index].title = firstUserMessage.text.substring(0, 30) + 
                                    (firstUserMessage.text.length > 30 ? '...' : '');
          }
        }
        this.chatHistories.set([...histories]);
      }
    }
  }

  handleKeyDown(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.sendMessage();
    }
  }

  // Remove the generateAIResponse method - it's not needed

  getChatsByTimeframe(timeframe: 'today' | 'yesterday' | 'week'): ChatHistory[] {
    const now = new Date();
    const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const yesterdayStart = new Date(todayStart.getTime() - 24 * 60 * 60 * 1000);
    const weekAgoStart = new Date(todayStart.getTime() - 7 * 24 * 60 * 60 * 1000);

    return this.chatHistories().filter(chat => {
      const chatTime = chat.timestamp.getTime();
      switch (timeframe) {
        case 'today':
          return chatTime >= todayStart.getTime();
        case 'yesterday':
          return chatTime >= yesterdayStart.getTime() && chatTime < todayStart.getTime();
        case 'week':
          return chatTime >= weekAgoStart.getTime() && chatTime < yesterdayStart.getTime();
        default:
          return false;
      }
    });
  }

  formatRelativeTime(date: Date): string {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (hours < 1) return 'Hace unos minutos';
    if (hours < 24) return `Hace ${hours} hora${hours > 1 ? 's' : ''}`;
    if (days === 1) return 'Ayer ' + date.toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' });
    if (days < 7) return `${days} días atrás`;
    return date.toLocaleDateString('es-CO');
  }

  formatNumber(num: number): string {
    return new Intl.NumberFormat('es-CO').format(num);
  }

  formatTimestamp(timestamp: string): string {
    return new Date(timestamp).toLocaleString('es-CO');
  }
}